import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path("d:/Mediclaim-Clean/backend").resolve()))

from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models import Claim, User, AuditLog, ClaimStatus

async def run_audit():
    async with AsyncSessionLocal() as session:
        # 1. Fetch or create mock user directly
        user_res = await session.execute(select(User).where(User.id == "local-dev-user"))
        user = user_res.scalars().first()
        if not user:
            print("User not found in DB! (this shouldn't happen if auth was successful)")
            return
        
        print(f"Mock User Org: {user.organization_id}")

        # 2. Simulate create_claim with None org
        import uuid
        def _uuid(): return str(uuid.uuid4())
        
        user_org_id = None # Mocking what happens if user.organization_id is None
        
        claim = Claim(
            claim_number="MC-TEST-8888",
            patient_name="Test Patient 2",
            notes="Audit test 2",
            status=ClaimStatus.DRAFT.value,
            organization_id=user_org_id,
            created_by_id=user.id,
        )
        session.add(claim)
        await session.commit()
        await session.refresh(claim)
        claim_id = claim.id
        print(f"Created Claim ID: {claim_id}")

        # Simulate AuditLog
        session.add(AuditLog(
            user_id=user.id,
            claim_id=claim.id,
            action="Claim created",
            entity_type="Claim",
            entity_id=claim.id,
        ))
        await session.commit()
        print("AuditLog committed.")

        # 3. Simulate upload_documents DB check
        result = await session.execute(
            select(Claim).where(Claim.id == claim_id, Claim.organization_id == user_org_id)
        )
        found_claim = result.scalar_one_or_none()
        if not found_claim:
            print(f"404 Not Found! Query: id={claim_id}, org={user_org_id}")
            
            # Why did it fail?
            raw = await session.execute(select(Claim.id, Claim.organization_id).where(Claim.id == claim_id))
            raw_claim = raw.first()
            if raw_claim:
                print(f"Claim actually exists! Real org: {raw_claim.organization_id}")
            else:
                print("Claim doesn't exist at all!")
        else:
            print("Success! Claim found for upload.")

if __name__ == "__main__":
    asyncio.run(run_audit())
