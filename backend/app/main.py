import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_db_and_tables
from pipeline import run_pipeline_for_prefix
from rules_loader import load_rules
from config import settings

app = FastAPI(title="Visual Audit Core Pipeline")

