# main.py
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_db_and_tables
from pipeline import run_pipeline_for_prefix
from rules_loader import load_rules
from config import settings

app = FastAPI(title="Visual Audit Core Pipeline")

# Load RULES on startup (optional)
RULES = load_rules()

@app.on_event("startup")
async def startup_event():
    # create tables if not exist (safe to call)
    await create_db_and_tables()

@app.get("/health")
async def health():
    return {"status": "ok", "env": {"s3_bucket": settings.s3_bucket, "aws_region": settings.aws_region}}

class RunAuditRequest(BaseModel):
    prefix: str
    rule_id: str
    store_id: str | None = None

@app.post("/run_audit")
async def run_audit(req: RunAuditRequest):
    """
    Run pipeline for all objects in prefix and a given rule_id.
    prefix: S3 prefix like "store123/2025-09-11/"
    rule_id: id of rule to evaluate (must exist in rules.json)
    """
    # basic validation
    rules = load_rules()
    if req.rule_id not in rules:
        raise HTTPException(status_code=400, detail=f"rule_id {req.rule_id} not found")

    # call pipeline (this returns after processing the objects)
    result = await run_pipeline_for_prefix(req.prefix, req.rule_id, req.store_id)
    return result

@app.get("/sample_rules")
async def sample_rules():
    # return loaded rule ids for quick check
    rules = load_rules()
    return {"count": len(rules), "rule_ids": list(rules.keys())}
