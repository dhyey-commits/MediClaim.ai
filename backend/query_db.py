import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

sys.path.insert(0, str(Path("d:/Mediclaim-Clean/backend").resolve()))

from app.database.database import AsyncSessionLocal
from app.models import AuditLog, Claim

async def investigate():
    async with AsyncSessionLocal() as db:
        # Find the latest EXTRACTION_FAILED claim
        res = await db.execute(
            select(Claim).where(Claim.status == 'EXTRACTION_FAILED').order_by(Claim.created_at.desc()).limit(1)
        )
        claim = res.scalar_one_or_none()
        
        if not claim:
            print("No EXTRACTION_FAILED claim found!")
            return
            
        print(f"Target Claim ID: {claim.id}")
        
        # Get all audit logs for this claim
        res_logs = await db.execute(
            select(AuditLog).where(AuditLog.claim_id == claim.id).order_by(AuditLog.created_at.asc())
        )
        logs = res_logs.scalars().all()
        
        for log in logs:
            print(f"[{log.created_at}] Action: {log.action} | Value: {log.new_value}")

if __name__ == "__main__":
    asyncio.run(investigate())
