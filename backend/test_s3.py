import asyncio
from app.s3_rek_client import list_objects
from app.config import settings

async def main():
    prefix = "audit-data/store123/CRE_Group_Photo/2025-09-08/"
    objects = await list_objects(prefix)
    print(f"Found {len(objects)} objects in S3 prefix '{prefix}'")
    for obj in objects[:5]:
        print(obj)

if __name__ == "__main__":
    asyncio.run(main())
