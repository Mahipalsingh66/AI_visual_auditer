import boto3
from botocore.config import Config
from io import BytesIO
from typing import List
from .config import settings

s3 = boto3.client("s3", region_name=settings.aws_region, config=Config(signature_version='s3v4'))

def list_objects(prefix: str, max_keys: int = 1000) -> List[dict]:
    """
    List objects under a prefix in the configured S3 bucket.
    Returns list of dicts with Key and LastModified.
    """
    bucket = settings.s3_bucket
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    objs = []
    for page in page_iterator:
        for obj in page.get("Contents", []):
            objs.append({"Key": obj["Key"], "LastModified": obj["LastModified"], "Size": obj["Size"]})
    return objs

def download_bytes(key: str) -> bytes:
    """Download object content as bytes."""
    bucket = settings.s3_bucket
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()
