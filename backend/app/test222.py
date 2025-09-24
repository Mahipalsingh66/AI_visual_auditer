import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image
import boto3

# ---------- CONFIG ----------
AWS_REGION = "ap-south-1"   # change if needed
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

rekognition = boto3.client("rekognition", region_name=AWS_REGION)

# ---------- RULES ----------
RULES = {
    "rule_faces": {
        "id": "rule_faces",
        "visual_audit_type": "FaceCount",
        "min_faces": 2
    },
    "rule_signage": {
        "id": "rule_signage",
        "visual_audit_type": "TextMatch",
        "expected_text": "POP IN"
    },
    "rule_label": {
        "id": "rule_label",
        "visual_audit_type": "LabelCheck",
        "expected_labels": ["Sign", "Poster", "Billboard"]
    }
}

# ---------- HELPERS ----------
def detect_faces_bytes(image_bytes: bytes):
    return rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['DEFAULT'])

def detect_labels_bytes(image_bytes: bytes):
    return rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=10, MinConfidence=70)

def detect_text_bytes(image_bytes: bytes):
    return rekognition.detect_text(Image={'Bytes': image_bytes})

# ---------- PIPELINE ----------
def run_visual_audit_local(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    results = {}
    for rule_id, rule in RULES.items():
        status, reason = "REVIEW", None
        try:
            if rule["visual_audit_type"] == "FaceCount":
                resp = detect_faces_bytes(image_bytes)
                count = len(resp.get("FaceDetails", []))
                if count >= rule.get("min_faces", 1):
                    status = "PASS"
                else:
                    status = "FAIL"
                    reason = f"face_count_{count}_lt_{rule['min_faces']}"

            elif rule["visual_audit_type"] == "TextMatch":
                resp = detect_text_bytes(image_bytes)
                texts = [t["DetectedText"].upper() for t in resp["TextDetections"]]
                expected = rule["expected_text"].upper()
                if any(expected in t for t in texts):
                    status = "PASS"
                else:
                    status = "FAIL"
                    reason = f"text_not_found_{expected}"

            elif rule["visual_audit_type"] == "LabelCheck":
                resp = detect_labels_bytes(image_bytes)
                labels = [l["Name"].upper() for l in resp["Labels"]]
                expected_labels = [e.upper() for e in rule["expected_labels"]]
                if all(e in labels for e in expected_labels):
                    status = "PASS"
                else:
                    status = "FAIL"
                    reason = "labels_missing"

        except Exception as e:
            status, reason = "ERROR", str(e)

        results[rule_id] = {"status": status, "reason": reason}

    return {
        "run_id": str(uuid.uuid4()),
        "image": image_path,
        "processed_at": datetime.utcnow().isoformat(),
        "results": results
    }

# ---------- MAIN ----------
def run_folder(folder_path: str):
    all_results = []
    folder = Path(folder_path)
    for file in folder.iterdir():
        if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            print(f"Processing {file} ...")
            result = run_visual_audit_local(str(file))
            all_results.append(result)
            # save json per image
            out_file = RESULTS_DIR / f"{file.stem}_result.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
    print(f"\n✅ Completed. Results saved in {RESULTS_DIR}")
    return all_results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python local_pipeline.py <image_folder>")
        sys.exit(1)

    run_folder(sys.argv[1])
