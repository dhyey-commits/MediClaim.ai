import asyncio
from app.database.database import engine
from app.database.base import Base
from app.models import Report

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init())
