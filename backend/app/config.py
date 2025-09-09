from pydantic import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "ap-south-1"
    s3_bucket: str
    database_url: str
    phash_hamming_threshold: int = 10
    recent_days: int = 30
    concurrency: int = 6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
