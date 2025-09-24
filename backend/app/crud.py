from database import AsyncSessionLocal
from models import Image, Audit
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, Any

async def upsert_image_record(record: Dict[str, Any]):
    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(Image).where(Image.s3_key == record["s3_key"]))
        existing = stmt.scalar_one_or_none()
        if existing:
            for k, v in record.items():
                if hasattr(existing, k) and v is not None:
                    setattr(existing, k, v)
            await session.commit()
            await session.refresh(existing)
            return existing
        else:
            new = Image(**record)
            session.add(new)
            await session.commit()
            await session.refresh(new)
            return new

async def insert_audit(audit: Dict[str, Any]):
    async with AsyncSessionLocal() as session:
        a = Audit(**audit)
        session.add(a)
        await session.commit()
        await session.refresh(a)
        return a

async def get_recent_images_phashes(prefix: str, days: int):
    cutoff = datetime.utcnow() - timedelta(days=days)
    async with AsyncSessionLocal() as session:
        stmt = select(Image.phash).where(Image.s3_key.like(f"{prefix}%"), Image.processed_at >= cutoff)
        res = await session.execute(stmt)
        return [r for r in res.scalars().all() if r]
