import asyncio, uuid
from datetime import datetime
from s3_rek_client import list_objects, get_object_bytes, detect_faces_bytes, detect_labels_bytes, detect_text_bytes
from image_utils import compute_phash, phash_hamming_distance
from crud import upsert_image_record, insert_audit, get_recent_images_phashes
from config import settings
from rules_loader import load_rules

RULES = load_rules()

async def _process_object(obj, rule_id, store_id, semaphore):
    async with semaphore:
        s3_key = obj["Key"]
        run_id = str(uuid.uuid4())
        processed_at = datetime.utcnow().isoformat()

        try:
            bytes_img = await get_object_bytes(s3_key)
        except Exception as e:
            await insert_audit({"run_id": run_id, "rule_id": rule_id, "s3_key": s3_key, "status": "ERROR", "reason": f"download_error:{e}", "processed_at": processed_at})
            return {"s3_key": s3_key, "status": "ERROR", "reason": str(e)}

        # phash
        try: phash = compute_phash(bytes_img)
        except: phash = None

        # duplicates
        recent_phashes = await get_recent_images_phashes(s3_key.rsplit("/", 2)[0]+"/", settings.recent_days)
        is_repeated = False
        if phash and recent_phashes:
            for old in recent_phashes:
                if phash_hamming_distance(phash, old) <= settings.phash_hamming_threshold:
                    is_repeated = True
                    break

        # rule
        rule = RULES.get(rule_id)
        rek_resp = {}
        face_count = None
        status = "REVIEW"
        reason = None

        if not rule:
            status = "REVIEW"
            reason = "no_rule_found"
        else:
            rtype = rule.get("visual_audit_type")
            if rtype == "FaceCount":
                rf = await detect_faces_bytes(bytes_img)
                face_count = len(rf.get("FaceDetails", []))
                rek_resp = rf
                if face_count >= rule.get("min_faces", 1): status="PASS"
                else: status="FAIL"; reason=f"face_count_{face_count}_lt_{rule.get('min_faces')}"
            elif rtype == "TextMatch":
                rt = await detect_text_bytes(bytes_img)
                texts = [t.get("DetectedText","").upper() for t in rt.get("TextDetections",[])]
                rek_resp = rt
                expected = rule.get("expected_text","").upper()
                if expected in " ".join(texts): status="PASS"
                else: status="FAIL"; reason=f"text_not_found_{expected}"
            elif rtype == "LabelCheck":
                rl = await detect_labels_bytes(bytes_img)
                labels = [l.get("Name") for l in rl.get("Labels",[])]
                rek_resp = rl
                expected = rule.get("expected_labels", [])
                if all(e in labels for e in expected): status="PASS"
                else: status="FAIL"; reason="labels_missing"
            else:
                status="REVIEW"; reason=f"unsupported_rule_type_{rtype}"

        if is_repeated:
            reason = (reason + "|REPEATED") if reason else "REPEATED"
            status="FAIL"

        # save
        record = {"s3_key": s3_key, "file_url": f"s3://{settings.s3_bucket}/{s3_key}", "rule_id": rule_id, "store_id": store_id, "captured_at": obj.get("LastModified").isoformat() if obj.get("LastModified") else None, "processed_at": processed_at, "phash": phash, "rekognition_json": rek_resp, "face_count": face_count, "is_repeated": is_repeated}
        await upsert_image_record(record)

        await insert_audit({"run_id": run_id, "rule_id": rule_id, "s3_key": s3_key, "status": status, "reason": reason, "processed_at": processed_at})
        return {"s3_key": s3_key, "status": status, "reason": reason, "is_repeated": is_repeated}

async def run_pipeline_for_prefix(prefix: str, rule_id: str, store_id: str = None):
    objs = await list_objects(prefix)
    cutoff_ts = datetime.utcnow().timestamp() - (settings.recent_days*24*3600)
    objs_recent = [o for o in objs if o.get("LastModified") and o["LastModified"].timestamp() >= cutoff_ts]

    sem = asyncio.Semaphore(settings.concurrency)
    tasks = [asyncio.create_task(_process_object(obj, rule_id, store_id, sem)) for obj in objs_recent]
    results = await asyncio.gather(*tasks)
    return {"prefix": prefix, "rule_id": rule_id, "processed": len(results), "results": results}
