import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

sys.path.insert(0, str(Path("d:/Mediclaim-Clean/backend").resolve()))

from app.database.database import AsyncSessionLocal
from app.models import OCRResult

async def investigate():
    claim_id = "06d35b7b-f151-4684-9e9e-f8290413e288"
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(OCRResult).where(OCRResult.claim_id == claim_id).order_by(OCRResult.page_number)
        )
        records = res.scalars().all()
        
        full_text = "\n\n".join([f"--- Page {record.page_number} ---\n{record.raw_text}" for record in records])
        print(f"Total OCR text length: {len(full_text)}")

if __name__ == "__main__":
    asyncio.run(investigate())
