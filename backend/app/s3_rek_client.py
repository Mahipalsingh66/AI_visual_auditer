import aioboto3
from .config import settings
from typing import List, Dict, Any

_session = aioboto3.Session()

async def list_objects(prefix: str) -> List[Dict[str, Any]]:
    bucket = settings.s3_bucket
    async with _session.client("s3", region_name=settings.aws_region) as s3:
        paginator = s3.get_paginator("list_objects_v2")
        objs = []
        async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                objs.append({"Key": o["Key"], "LastModified": o["LastModified"], "Size": o["Size"]})
        return objs

async def get_object_bytes(key: str) -> bytes:
    bucket = settings.s3_bucket
    async with _session.client("s3", region_name=settings.aws_region) as s3:
        resp = await s3.get_object(Bucket=bucket, Key=key)
        return await resp["Body"].read()

async def detect_labels_bytes(image_bytes: bytes, min_confidence: int = 70, max_labels: int = 20) -> Dict[str, Any]:
    async with _session.client("rekognition", region_name=settings.aws_region) as rek:
        return await rek.detect_labels(Image={"Bytes": image_bytes}, MinConfidence=min_confidence, MaxLabels=max_labels)

async def detect_faces_bytes(image_bytes: bytes) -> Dict[str, Any]:
    async with _session.client("rekognition", region_name=settings.aws_region) as rek:
        return await rek.detect_faces(Image={"Bytes": image_bytes}, Attributes=["ALL"])

async def detect_text_bytes(image_bytes: bytes) -> Dict[str, Any]:
    async with _session.client("rekognition", region_name=settings.aws_region) as rek:
        return await rek.detect_text(Image={"Bytes": image_bytes})
