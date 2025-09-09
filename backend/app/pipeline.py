import uuid
from datetime import datetime
from typing import Dict, Any
from .s3_fetcher import list_objects, download_bytes
from .image_utils import compute_phash, phash_hamming_distance
from .rekognition_client import detect_faces_bytes, detect_labels_bytes, detect_text_bytes
from .db import upsert_image_record, insert_audit, get_images_within_days
from .config import settings
import json

# Example simple rule mapping:
# You should map your real rules table (rule_id -> visual_audit_type and parameters)
DEFAULT_RULES = {
    # rule_id: {type: .., params: ...}
    "rule_1": {"type": "FaceCount", "min_faces": 2},
    "rule_2": {"type": "TextMatch", "expected_text": "POP IN"},
    "rule_3": {"type": "LabelCheck", "expected_labels": ["Building","Sign"]}
}

def run_pipeline_for_prefix(prefix: str, rule_id: str, store_id: str = None) -> Dict[str, Any]:
    """
    Main orchestration:
    - list objects under prefix
    - for each object: download, compute phash, run rekognition checks,
      check against last RECENT_DAYS images for repeats by phash hamming distance,
      store results into DB and audits
    """
    run_id = str(uuid.uuid4())
    objects = list_objects(prefix)
    results = []
    rule = DEFAULT_RULES.get(rule_id)
    if rule is None:
        raise ValueError(f"No rule mapping found for {rule_id}")

    # get prior images within recent window (prefix could be store-specific)
    recent_items = get_images_within_days(prefix, settings.recent_days)
    recent_phashes = [r["phash"] for r in recent_items if r.get("phash")]

    for obj in objects:
        s3_key = obj["Key"]
        try:
            img_bytes = download_bytes(s3_key)
        except Exception as e:
            insert_audit({
                "run_id": run_id, "rule_id": rule_id, "s3_key": s3_key,
                "status": "ERROR", "reason": f"download_error:{e}", "processed_at": datetime.utcnow().isoformat()
            })
            continue

        processed_at = datetime.utcnow().isoformat()
        phash = compute_phash(img_bytes)
        is_repeated = False
        # Compare with recent phashes
        for old_ph in recent_phashes:
            dist = phash_hamming_distance(phash, old_ph)
            if dist <= settings.phash_hamming_threshold:
                is_repeated = True
                break

        rek_resp = {}
        face_count = None
        status = "REVIEW"
        reason = None

        # Apply rule checks
        if rule["type"] == "FaceCount":
            rf = detect_faces_bytes(img_bytes)
            face_count = len(rf.get("FaceDetails", []))
            rek_resp = rf
            if face_count >= rule.get("min_faces", 1):
                status = "PASS"
            else:
                status = "FAIL"
                reason = f"face_count_{face_count}_lt_{rule.get('min_faces')}"
        elif rule["type"] == "TextMatch":
            rt = detect_text_bytes(img_bytes)
            texts = [t.get("DetectedText","").upper() for t in rt.get("TextDetections",[])]
            rek_resp = rt
            expected = rule.get("expected_text","").upper()
            if expected in texts:
                status = "PASS"
            else:
                status = "FAIL"
                reason = f"text_not_found_{expected}"
        elif rule["type"] == "LabelCheck":
            rl = detect_labels_bytes(img_bytes)
            labels = [l.get("Name") for l in rl.get("Labels",[])]
            rek_resp = rl
            expected_labels = rule.get("expected_labels", [])
            if all(e in labels for e in expected_labels):
                status = "PASS"
            else:
                status = "FAIL"
                reason = f"labels_missing"
        else:
            status = "REVIEW"
            rek_resp = {"info": "unknown_rule_type"}

        # If repeated, prefer marking reason
        if is_repeated:
            reason = (reason + "|REPEATED") if reason else "REPEATED"
            # business decision: consider repeated as FAIL or REVIEW; here we set flag and keep original status
            # override status to FAIL if you want:
            status = "FAIL"

        # store image metadata
        record = {
            "s3_key": s3_key,
            "file_url": f"s3://{settings.s3_bucket}/{s3_key}",
            "rule_id": rule_id,
            "store_id": store_id,
            "captured_at": obj["LastModified"].isoformat() if hasattr(obj["LastModified"], "isoformat") else None,
            "processed_at": processed_at,
            "phash": phash,
            "rekognition_json": json.dumps(rek_resp),
            "face_count": face_count,
            "is_repeated": is_repeated
        }
        upsert_image_record(record)

        insert_audit({
            "run_id": run_id, "rule_id": rule_id, "s3_key": s3_key,
            "status": status, "reason": reason,
            "processed_at": processed_at
        })

        results.append({
            "s3_key": s3_key, "status": status, "reason": reason,
            "is_repeated": is_repeated, "phash": phash
        })

    return {"run_id": run_id, "prefix": prefix, "rule_id": rule_id, "items_processed": len(results), "results": results}
