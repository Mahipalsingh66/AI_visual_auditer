visual_audit_project/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                # FastAPI app (endpoints)
│  │  ├─ config.py              # env/config loader
│  │  ├─ s3_fetcher.py          # list/download files from S3
│  │  ├─ rekognition_client.py  # Rekognition wrappers
│  │  ├─ image_utils.py         # pHash, image helpers
│  │  ├─ db.py                  # SQLite DB access (audits + images)
│  │  ├─ pipeline.py            # Orchestration for checking S3 folder & 30-day duplicates
│  │  └─ requirements.txt
└─ README.md