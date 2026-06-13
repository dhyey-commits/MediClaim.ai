import asyncio
from sqlalchemy.future import select
from app.database.database import AsyncSessionLocal
from app.models import BenchmarkRun

async def dump():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(BenchmarkRun))
        runs = res.scalars().all()
        for r in runs[:2]:
            print(f"ID: {r.id}")
            print(f"Doc: {r.document_source}")
            print(f"Metrics: {r.metrics_json}")
            print("---")

if __name__ == "__main__":
    asyncio.run(dump())
