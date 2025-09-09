import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "")
    db_path: str = os.getenv("DB_PATH", "./audit_store.db")
    phash_hamming_threshold: int = int(os.getenv("PHASH_HAMMING_THRESHOLD", "10"))
    recent_days: int = int(os.getenv("RECENT_DAYS", "30"))

settings = Settings()
