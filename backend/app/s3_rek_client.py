# s3_rek_client.py
import boto3
from botocore.config import Config
import asyncio
from typing import List, Dict, Any
from io import BytesIO
from config import settings

# Create boto3 clients (synchronous)
_s3 = boto3.client("s3", region_name=settings.aws_region, config=Config(signature_version='s3v4'))
_rek = boto3.client("rekognition", region_name=settings.aws_region, config=Config(retries={'max_attempts': 3}))

# -------------------------
# Helper to run blocking boto3 calls in thread
# -------------------------
async def _to_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)

# -------------------------
# S3 helpers (async)
# -------------------------
async def list_objects(prefix: str, max_keys: int = 1000) -> List[Dict[str, Any]]:
    """
    List objects under a prefix in the configured S3 bucket.
    Returns list of dicts with Key and LastModified.
    """
    bucket = settings.s3_bucket

    def _list():
        paginator = _s3.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
        objs = []
        for page in page_iterator:
            for obj in page.get("Contents", []):
                objs.append({"Key": obj["Key"], "LastModified": obj["LastModified"], "Size": obj.get("Size")})
        return objs

    return await _to_thread(_list)

async def get_object_bytes(key: str) -> bytes:
    """Download object content as bytes."""
    bucket = settings.s3_bucket

    def _get():
        resp = _s3.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()

    return await _to_thread(_get)

# -------------------------
# Rekognition wrappers (async)
# -------------------------
async def detect_faces_bytes(image_bytes: bytes, attributes: list = None) -> dict:
    """
    Returns Rekognition detect_faces response for given image bytes.
    """
    if attributes is None:
        attributes = ['DEFAULT']

    def _call():
        return _rek.detect_faces(Image={'Bytes': image_bytes}, Attributes=attributes)

    return await _to_thread(_call)

async def detect_labels_bytes(image_bytes: bytes, max_labels: int = 20, min_confidence: int = 70) -> dict:
    """
    Returns Rekognition detect_labels response for given image bytes.
    """
    def _call():
        return _rek.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=max_labels, MinConfidence=min_confidence)

    return await _to_thread(_call)

async def detect_text_bytes(image_bytes: bytes) -> dict:
    """
    Returns Rekognition detect_text response for given image bytes.
    """
    def _call():
        return _rek.detect_text(Image={'Bytes': image_bytes})

    return await _to_thread(_call)

async def detect_faces_s3(bucket: str, key: str, attributes: list = None) -> dict:
    if attributes is None:
        attributes = ['DEFAULT']
    def _call():
        return _rek.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': key}}, Attributes=attributes)
    return await _to_thread(_call)

async def detect_labels_s3(bucket: str, key: str, max_labels: int = 20, min_confidence: int = 70) -> dict:
    def _call():
        return _rek.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}}, MaxLabels=max_labels, MinConfidence=min_confidence)
    return await _to_thread(_call)

async def detect_text_s3(bucket: str, key: str) -> dict:
    def _call():
        return _rek.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': key}})
    return await _to_thread(_call)
