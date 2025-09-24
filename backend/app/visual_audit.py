# import boto3
# import os
# import json

# # ---------- CONFIG ----------
# AWS_REGION = "ap-south-1"   # change to your AWS region
# # Make sure AWS credentials are set in environment (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# # ---------- SAMPLE RULES ----------
# rules = [
#     {
#         "id": "rule_cre_group",
#         "group": "Morning Meeting",
#         "section": "CRE Morning Meeting",
#         "sub_section": "Morning Briefing Time",
#         "norms": "CRE group photo must be submitted as per guideline",
#         "visual_audit_type": "FaceCount",
#         "min_faces": 2
#     },
#     {
#         "id": "rule_signage",
#         "group": "Store Front",
#         "section": "Signage",
#         "sub_section": "POP IN Sticker",
#         "norms": "POP IN sticker must be visible",
#         "visual_audit_type": "TextCheck",
#         "text_required": "POP IN"
#     }
# ]

# # ---------- AWS CLIENT ----------
# rekognition = boto3.client("rekognition", region_name=AWS_REGION)


# # ---------- HELPERS ----------
# def run_face_count(image_bytes, rule):
#     resp = rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['DEFAULT'])
#     face_count = len(resp['FaceDetails'])
#     print(f"Detected {face_count} faces")
#     return face_count >= rule["min_faces"]


# def run_text_check(image_bytes, rule):
#     resp = rekognition.detect_text(Image={'Bytes': image_bytes})
#     detected_texts = [d['DetectedText'] for d in resp['TextDetections']]
#     print("Detected texts:", detected_texts)
#     return any(rule["text_required"].lower() in t.lower() for t in detected_texts)


# def run_object_check(image_bytes, rule):
#     resp = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=10, MinConfidence=70)
#     labels = [label['Name'] for label in resp['Labels']]
#     print("Detected labels:", labels)
#     return rule["object_required"].lower() in [l.lower() for l in labels]

# # image_path = "C:/Users/QD2220/Downloads/1756980399.jpg"  # replace with your test image path


# # ---------- MAIN PIPELINE ----------
# def run_visual_audit(image_path):
#     with open(image_path, "rb") as f:
#         image_bytes = f.read()

#     results = {}
#     for rule in rules:
#         if rule["visual_audit_type"] == "FaceCount":
#             results[rule["id"]] = run_face_count(image_bytes, rule)
#         elif rule["visual_audit_type"] == "TextCheck":
#             results[rule["id"]] = run_text_check(image_bytes, rule)
#         elif rule["visual_audit_type"] == "ObjectDetection":
#             results[rule["id"]] = run_object_check(image_bytes, rule)
#         else:
#             results[rule["id"]] = "Unsupported Rule"

#     return results


# if __name__ == "__main__":
#     # Example: python visual_audit.py test_image.jpg
#     import sys
#     if len(sys.argv) < 2:
#         print("Usage: python visual_audit.py <image_path>")
#         sys.exit(1)

#     image_path = sys.argv[1]
#     if not os.path.exists(image_path):
#         print(f"File not found: {image_path}")
#         sys.exit(1)

#     audit_results = run_visual_audit(image_path)
#     print("\n=== FINAL AUDIT RESULTS ===")
#     print(json.dumps(audit_results, indent=2))
import boto3
import os
import json

# ---------- CONFIG ----------
AWS_REGION = "ap-south-1"   # change to your AWS region

# ---------- SAMPLE RULES ----------
rules = [
    {
        "id": "rule_cre_group",
        "group": "Morning Meeting",
        "section": "CRE Morning Meeting",
        "sub_section": "Morning Briefing Time",
        "norms": "CRE group photo must be submitted as per guideline",
        "visual_audit_type": "FaceCount",
        "min_faces": 2
    },
    {
        "id": "rule_signage",
        "group": "Store Front",
        "section": "Signage",
        "sub_section": "POP IN Sticker",
        "norms": "POP IN sticker must be visible",
        "visual_audit_type": "TextCheck",
        "text_required": "POP IN"
    },
    {
        "id": "rule_photo_quality",
        "group": "Generic",
        "section": "Photo Submission",
        "sub_section": "Image Quality",
        "norms": "Photo must be uploaded correctly with proper angle",
        "visual_audit_type": "PhotoPresence"
    }
]

# ---------- AWS CLIENT ----------
rekognition = boto3.client("rekognition", region_name=AWS_REGION)


# ---------- HELPERS ----------
def run_face_count(image_bytes, rule):
    resp = rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['DEFAULT'])
    face_count = len(resp['FaceDetails'])
    print(f"Detected {face_count} faces")
    return face_count >= rule["min_faces"]


def run_text_check(image_bytes, rule):
    resp = rekognition.detect_text(Image={'Bytes': image_bytes})
    detected_texts = [d['DetectedText'] for d in resp['TextDetections']]
    print("Detected texts:", detected_texts)
    return any(rule["text_required"].lower() in t.lower() for t in detected_texts)


def run_object_check(image_bytes, rule):
    resp = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=10, MinConfidence=70)
    labels = [label['Name'] for label in resp['Labels']]
    print("Detected labels:", labels)
    return rule["object_required"].lower() in [l.lower() for l in labels]


def run_photo_presence(image_bytes, rule):
    resp = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=5, MinConfidence=70)
    labels = [label['Name'] for label in resp['Labels']]
    orientation = resp.get("OrientationCorrection", "UP")
    print("Detected labels (for presence):", labels)
    print("Orientation Correction:", orientation)

    # Check: at least something meaningful detected, and orientation is OK
    return (len(labels) > 0) and (orientation in ["UP", "ROTATE_0"])


# ---------- MAIN PIPELINE ----------
def run_visual_audit(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    results = {}
    for rule in rules:
        if rule["visual_audit_type"] == "FaceCount":
            results[rule["id"]] = run_face_count(image_bytes, rule)
        elif rule["visual_audit_type"] == "TextCheck":
            results[rule["id"]] = run_text_check(image_bytes, rule)
        elif rule["visual_audit_type"] == "ObjectDetection":
            results[rule["id"]] = run_object_check(image_bytes, rule)
        elif rule["visual_audit_type"] == "PhotoPresence":
            results[rule["id"]] = run_photo_presence(image_bytes, rule)
        else:
            results[rule["id"]] = "Unsupported Rule"

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python visual_audit.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)

    audit_results = run_visual_audit(image_path)
    print("\n=== FINAL AUDIT RESULTS ===")
    print(json.dumps(audit_results, indent=2))
