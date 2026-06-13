import asyncio
from sqlalchemy.future import select
from app.database.database import AsyncSessionLocal
from app.models import BenchmarkRun

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(BenchmarkRun))
        runs = res.scalars().all()
        print(f"Total benchmark runs: {len(runs)}")

if __name__ == "__main__":
    asyncio.run(check())
