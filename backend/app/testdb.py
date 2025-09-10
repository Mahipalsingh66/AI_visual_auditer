import asyncio
from database import create_db_and_tables

asyncio.run(create_db_and_tables())
print("✅ Tables created successfully")

# import asyncio
# from sqlalchemy.ext.asyncio import create_async_engine

# DATABASE_URL = "postgresql+asyncpg://postgres:Mahipal%406695@localhost:5432/visual_audit"

# engine = create_async_engine(DATABASE_URL, echo=True)

# async def create_table():
#     async with engine.begin() as conn:
#         await conn.execute("""
#             CREATE TABLE IF NOT EXISTS audit_rules (
#                 id SERIAL PRIMARY KEY,
#                 group_area VARCHAR(100),
#                 section VARCHAR(100),
#                 sub_section VARCHAR(100),
#                 norms TEXT,
#                 reference_image VARCHAR(255),
#                 question TEXT,
#                 min_options INT,
#                 max_options INT,
#                 audit_type VARCHAR(50),
#                 remarks TEXT
#             );
#         """)
#     print("✅ Table created successfully!")

# asyncio.run(create_table())
