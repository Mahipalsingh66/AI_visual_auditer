import boto3
from botocore.config import Config
from typing import Dict, Any
from .config import settings

rek = boto3.client("rekognition", region_name=settings.aws_region, config=Config(retries={'max_attempts': 3}))

def detect_faces_bytes(image_bytes: bytes) -> Dict[str, Any]:
    return rek.detect_faces(Image={"Bytes": image_bytes}, Attributes=["DEFAULT"])

def detect_labels_bytes(image_bytes: bytes, min_confidence: int = 70, max_labels: int = 20) -> Dict[str, Any]:
    return rek.detect_labels(Image={"Bytes": image_bytes}, MinConfidence=min_confidence, MaxLabels=max_labels)

def detect_text_bytes(image_bytes: bytes) -> Dict[str, Any]:
    return rek.detect_text(Image={"Bytes": image_bytes})

def compare_faces_bytes(source_bytes: bytes, target_bytes: bytes, similarity_threshold: float = 80.0) -> Dict[str, Any]:
    return rek.compare_faces(SourceImage={"Bytes": source_bytes}, TargetImage={"Bytes": target_bytes}, SimilarityThreshold=similarity_threshold)
