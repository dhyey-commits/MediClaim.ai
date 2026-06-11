import httpx
import asyncio

async def test_ocr():
    async with httpx.AsyncClient() as client:
        # Create a claim
        resp = await client.post('http://localhost:8000/claims', json={'patient_name': 'Test OCR Patient', 'notes': 'Diagnosing OCR issue'})
        if resp.status_code != 200 and resp.status_code != 201:
            print(f'Failed to create claim: {resp.text}')
            return
        
        claim_id = resp.json()['id']
        print(f'Created claim: {claim_id}')
        
        # Trigger OCR
        print(f'Triggering OCR for {claim_id}...')
        ocr_resp = await client.post(f'http://localhost:8000/claims/{claim_id}/ocr')
        print(f'OCR Response Status: {ocr_resp.status_code}')
        print(f'OCR Response Body: {ocr_resp.text}')

asyncio.run(test_ocr())
