import asyncio
from sqlalchemy.future import select
from app.database.database import AsyncSessionLocal
from app.models import Claim

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Claim))
        claims = res.scalars().all()
        print(f"Total claims: {len(claims)}")
        for c in claims:
            print(f"Claim ID: {c.id}")

if __name__ == "__main__":
    asyncio.run(check())
