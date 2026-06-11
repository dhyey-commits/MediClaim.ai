import httpx
import asyncio
import io

async def test_ocr():
    async with httpx.AsyncClient() as client:
        # Create a claim
        resp = await client.post('http://localhost:8000/claims', json={'patient_name': 'Test OCR Patient', 'notes': 'Diagnosing OCR issue'})
        if resp.status_code not in (200, 201):
            print(f'Failed to create claim: {resp.text}')
            return
        
        claim_id = resp.json()['id']
        print(f'Created claim: {claim_id}')
        
        # Upload a dummy image to the claim
        # We need a small valid image to be uploaded
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        files = {'files': ('dummy.png', img_byte_arr, 'image/png')}
        upload_resp = await client.post(f'http://localhost:8000/claims/{claim_id}/upload', files=files)
        print(f'Upload response: {upload_resp.status_code}')
        
        # Trigger OCR
        print(f'Triggering OCR for {claim_id}...')
        ocr_resp = await client.post(f'http://localhost:8000/claims/{claim_id}/ocr')
        print(f'OCR Response Status: {ocr_resp.status_code}')
        print(f'OCR Response Body: {ocr_resp.text}')
        
        # Poll for completion
        print('Polling for OCR completion...')
        for _ in range(15):
            await asyncio.sleep(2)
            check_resp = await client.get(f'http://localhost:8000/claims/{claim_id}')
            claim_status = check_resp.json()['status']
            print(f'Claim status: {claim_status}')
            if claim_status in ('OCR_COMPLETE', 'OCR_FAILED'):
                break
                
        # Check OCR results
        res_resp = await client.get(f'http://localhost:8000/claims/{claim_id}/ocr')
        print(f'OCR Results: {res_resp.text}')

asyncio.run(test_ocr())
