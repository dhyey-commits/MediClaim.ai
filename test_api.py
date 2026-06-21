import asyncio
import httpx
import time

async def run_test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Mock auth header
        headers = {"Authorization": "Bearer mock-token"}
        
        # 1. Create Claim
        print("--- POST /claims ---")
        res_create = await client.post("/claims", json={"patient_name": "Test", "notes": "Forensic test"}, headers=headers)
        print("Create Status:", res_create.status_code)
        print("Create Response:", res_create.text)
        if res_create.status_code != 201:
            return
            
        claim_id = res_create.json()["id"]
        
        # 2. Upload Document
        print(f"--- POST /claims/{claim_id}/upload ---")
        files = {'files': ('test.pdf', b'fake pdf content', 'application/pdf')}
        res_upload = await client.post(f"/claims/{claim_id}/upload", files=files, headers=headers)
        print("Upload Status:", res_upload.status_code)
        print("Upload Response:", res_upload.text)

if __name__ == "__main__":
    asyncio.run(run_test())
