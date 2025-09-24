# import os, uuid
# from datetime import datetime
# from PIL import Image
# import asyncio

# from image_utils import compute_phash, phash_hamming_distance
# from s3_rek_client import detect_faces_bytes, detect_labels_bytes, detect_text_bytes
# from rules_loader import load_rules

# # load rules.json
# RULES = load_rules()

# async def process_local_image(img_path, id):
#     run_id = str(uuid.uuid4())
#     processed_at = datetime.utcnow().isoformat()

#     with open(img_path, "rb") as f:
#         img_bytes = f.read()

#     # compute phash
#     try:
#         phash = compute_phash(img_bytes)
#     except:
#         phash = None

#     # rule fetch
#     rule = RULES.get(id)
#     rek_resp = {}
#     face_count = None
#     status = "REVIEW"
#     reason = None

#     if not rule:
#         status = "REVIEW"
#         reason = "no_rule_found"
#     else:
#         rtype = rule.get("visual_audit_type")
#         if rtype == "FaceCount":
#             rf = await detect_faces_bytes(img_bytes)
#             face_count = len(rf.get("FaceDetails", []))
#             rek_resp = rf
#             if face_count >= rule.get("min_faces", 1):
#                 status = "PASS"
#             else:
#                 status = "FAIL"
#                 reason = f"face_count_{face_count}_lt_{rule.get('min_faces')}"
#         elif rtype == "TextMatch":
#             rt = await detect_text_bytes(img_bytes)
#             texts = [t.get("DetectedText","").upper() for t in rt.get("TextDetections",[])]
#             rek_resp = rt
#             expected = rule.get("expected_text","").upper()
#             if expected in " ".join(texts):
#                 status = "PASS"
#             else:
#                 status = "FAIL"
#                 reason = f"text_not_found_{expected}"
#         elif rtype == "LabelCheck":
#             rl = await detect_labels_bytes(img_bytes)
#             labels = [l.get("Name") for l in rl.get("Labels",[])]
#             rek_resp = rl
#             expected = rule.get("expected_labels", [])
#             if all(e in labels for e in expected):
#                 status = "PASS"
#             else:
#                 status = "FAIL"
#                 reason = "labels_missing"
#         else:
#             status = "REVIEW"
#             reason = f"unsupported_rule_type_{rtype}"

#     return {
#         "image": img_path,
#         "status": status,
#         "reason": reason,
#         "face_count": face_count,
#         "id": id,
#         "rekognition": rek_resp
#     }

# async def run_local_pipeline(folder_path, id):
#     imgs = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
#             if f.lower().endswith((".jpg", ".jpeg", ".png"))]

#     results = []
#     for img in imgs:
#         res = await process_local_image(img, id)
#         results.append(res)
#         print(f"[{res['status']}] {img} | Reason: {res['reason']}")

#     return results


# if __name__ == "__main__":
#     folder = r"C:\Users\QD2220\Downloads\Images_20250911_113537\Signage Images"  # 👈 yaha apna local folder path do
#     id = "rule_signage_vi_logo"                   # 👈 rules.json se ek rule ka id do
#     asyncio.run(run_local_pipeline(folder, id))
import os
import asyncio
import boto3
from datetime import datetime, timezone

# ---------------------- CONFIG ----------------------
AWS_REGION = "ap-south-1"  # change to your region
IMAGE_FOLDER = r"D:\AI_visual_auditer\AI_visual_auditer\Images\Signage Images"  # your folder path

# ---------------------- SINGLE RULE ----------------------
rule_signage_vi_logo = {
    "id": "rule_signage_vi_logo",
    "group": "Signage",
    "section": "Store Front",
    "sub_section": "Vi Logo / Sticker",
    "norms": "Check that any signage/sticker/logo is present and clearly visible.",
    "reference_image": None,              # optional, can be None
    "question": "Capture a photo of the entrance showing any signage/sticker/logo.",
    "options": "Min1 Max1",
    "visual_audit_type": "LabelDetection", # simple label detection
    "expected_labels": ["Sign", "Signage", "Sticker", "Logo"], # generic labels Rekognition can detect
    "min_confidence": 60.0,               # confidence threshold
    "remarks": "Just check for presence and clarity of signage/sticker/logo."
}



# ---------------------- AWS REKOGNITION CLIENT ----------------------
rekognition = boto3.client("rekognition", region_name=AWS_REGION)

# ---------------------- PROCESS SINGLE IMAGE ----------------------
async def process_image(img_path, rule):
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    # Rekognition detect_labels
    response = rekognition.detect_labels(
        Image={"Bytes": img_bytes},
        MaxLabels=20,
        MinConfidence=rule["min_confidence"]
    )

    # Check for expected label
    expected_label = rule["expected_labels"][0]
    found = False
    confidence = 0.0

    for label in response.get("Labels", []):
        if label["Name"].lower() == expected_label.lower():
            found = True
            confidence = label.get("Confidence", 0.0)
            break

    # Determine status
    status = "PASS" if found and confidence >= rule["min_confidence"] else "FAIL"
    reason = None if status == "PASS" else "Vi logo missing or unclear"

    # Timestamp
    processed_at = datetime.now(timezone.utc).isoformat()

    return {
        "image": img_path,
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "rule_id": rule["id"],
        "processed_at": processed_at,
        "rekognition_response": response
    }

# ---------------------- RUN PIPELINE ----------------------
async def run_pipeline(folder_path, rule):
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    results = []
    for img in images:
        res = await process_image(img, rule)
        results.append(res)
        print(f"[{res['status']}] {img} | Confidence: {res['confidence']:.2f} | Reason: {res['reason']}")

    return results

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    asyncio.run(run_pipeline(IMAGE_FOLDER, rule_signage_vi_logo))
