from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket: str
    database_url: str
    phash_hamming_threshold: int = 10
    recent_days: int = 30
    concurrency: int = 6

    class Config:
        env_file = str(Path(__file__).parent / ".env")  # points to backend/app/.env
        extra = "allow"

settings = Settings()
