from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    s3_key = Column(String, unique=True, nullable=False, index=True)
    file_url = Column(String)
    rule_id = Column(String, index=True)
    store_id = Column(String, index=True)
    captured_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, server_default=func.now())
    phash = Column(String, index=True)
    rekognition_json = Column(JSONB, nullable=True)
    face_count = Column(Integer, nullable=True)
    is_repeated = Column(Boolean, default=False)

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    rule_id = Column(String, index=True)
    s3_key = Column(String, index=True)
    status = Column(String)
    reason = Column(Text, nullable=True)
    processed_at = Column(DateTime, server_default=func.now())
