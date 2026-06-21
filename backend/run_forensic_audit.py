import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path("d:/Mediclaim-Clean/backend").resolve()))

from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models import Claim, User
from app.api.claims import create_claim, upload_documents
from app.schemas.claims import ClaimCreateRequest
from fastapi import UploadFile
import io

async def run_audit():
    async with AsyncSessionLocal() as session:
        # 1. Setup mock user
        mock_user = User(
            id="local-dev-user",
            email="local@dev.com",
            organization_id="local-dev-org",
            role="admin"
        )
        
        # 2. Call create_claim
        print("--- CALLING create_claim ---")
        req = ClaimCreateRequest(patient_name="Test Patient", notes="Audit test")
        try:
            res_create = await create_claim(body=req, db=session, current_user=mock_user)
            print("Create result:", res_create)
            claim_id = res_create["id"]
        except Exception as e:
            print("Create failed:", repr(e))
            return
            
        # 3. Query DB manually to verify
        result = await session.execute(
            select(Claim.id, Claim.claim_number, Claim.organization_id, Claim.created_by_id)
            .where(Claim.id == claim_id)
        )
        raw_claim = result.first()
        print("--- DB AFTER CREATE ---")
        print(f"ID: {raw_claim.id}, Org: {raw_claim.organization_id}, Creator: {raw_claim.created_by_id}")

        # 4. Call upload_documents
        print(f"--- CALLING upload_documents for claim_id: {claim_id} ---")
        dummy_file = UploadFile(filename="test.pdf", file=io.BytesIO(b"fake pdf"))
        try:
            res_upload = await upload_documents(claim_id=claim_id, files=[dummy_file], db=session, current_user=mock_user)
            print("Upload result:", res_upload)
        except Exception as e:
            print("Upload failed:", repr(e))

if __name__ == "__main__":
    asyncio.run(run_audit())
