import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .config import settings

def init_db():
    conn = sqlite3.connect(settings.db_path)
    cur = conn.cursor()
    # images table stores metadata per image
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        s3_key TEXT UNIQUE,
        file_url TEXT,
        rule_id TEXT,
        store_id TEXT,
        captured_at TEXT,
        processed_at TEXT,
        phash TEXT,
        rekognition_json TEXT,
        face_count INTEGER,
        is_repeated INTEGER DEFAULT 0
    )
    """)
    # audits table stores per-run summary
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT,
        rule_id TEXT,
        s3_key TEXT,
        status TEXT,
        reason TEXT,
        processed_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def upsert_image_record(record: Dict[str, Any]):
    conn = sqlite3.connect(settings.db_path)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO images (s3_key, file_url, rule_id, store_id, captured_at, processed_at, phash, rekognition_json, face_count, is_repeated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["s3_key"],
        record.get("file_url"),
        record.get("rule_id"),
        record.get("store_id"),
        record.get("captured_at"),
        record.get("processed_at"),
        record.get("phash"),
        record.get("rekognition_json"),
        record.get("face_count"),
        1 if record.get("is_repeated") else 0
    ))
    conn.commit()
    conn.close()

def insert_audit(audit: Dict[str, Any]):
    conn = sqlite3.connect(settings.db_path)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO audits (run_id, rule_id, s3_key, status, reason, processed_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        audit.get("run_id"),
        audit.get("rule_id"),
        audit.get("s3_key"),
        audit.get("status"),
        audit.get("reason"),
        audit.get("processed_at")
    ))
    conn.commit()
    conn.close()

def get_images_within_days(prefix: str, days: int) -> List[Dict[str,Any]]:
    conn = sqlite3.connect(settings.db_path)
    cur = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    cur.execute("""
    SELECT s3_key, phash, processed_at FROM images
    WHERE s3_key LIKE ? AND processed_at >= ?
    """, (f"{prefix}%", cutoff))
    rows = cur.fetchall()
    conn.close()
    return [{"s3_key": r[0], "phash": r[1], "processed_at": r[2]} for r in rows]

def query_recent_duplicates(prefix: str, days: int):
    conn = sqlite3.connect(settings.db_path)
    cur = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    cur.execute("""
    SELECT s3_key, phash, processed_at, is_repeated FROM images
    WHERE s3_key LIKE ? AND processed_at >= ?
    ORDER BY processed_at DESC
    """, (f"{prefix}%", cutoff))
    rows = cur.fetchall()
    conn.close()
    return [{"s3_key": r[0], "phash": r[1], "processed_at": r[2], "is_repeated": bool(r[3])} for r in rows]
