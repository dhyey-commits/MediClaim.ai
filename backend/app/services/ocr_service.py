import asyncio
import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from paddleocr import PaddleOCR
import logging

from app.models import Claim, Document, OCRResult, DocumentStatus, ClaimStatus, AuditLog

logger = logging.getLogger(__name__)

# Initialize PaddleOCR globally to avoid reloading weights on every invocation.
# use_angle_cls=True helps with rotated text, lang='en' for English
try:
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
except Exception as e:
    logger.error(f"Failed to initialize PaddleOCR: {e}")
    ocr_engine = None

async def run_ocr_for_claim(claim_id: str, db: AsyncSession):
    """
    Background task to run OCR on all pending/failed documents for a claim.
    """
    if ocr_engine is None:
        logger.error("PaddleOCR is not initialized. Aborting OCR.")
        return

    # Fetch claim and its documents
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    
    if not claim:
        logger.error(f"Claim {claim_id} not found.")
        return
        
    result = await db.execute(select(Document).where(Document.claim_id == claim_id))
    documents = result.scalars().all()
    
    docs_to_process = [d for d in documents if d.status in (DocumentStatus.PENDING.value, DocumentStatus.FAILED.value)]
    
    if not docs_to_process:
        logger.info(f"No documents to process for claim {claim_id}")
        return

    claim.status = ClaimStatus.OCR_PROCESSING.value
    await db.commit()
    
    total_extracted = 0
    
    try:
        for doc in docs_to_process:
            doc.status = DocumentStatus.OCR_PROCESSING.value
            await db.commit()
            
            extracted_text = ""
            try:
                # Need to read the file to bytes. (Assuming doc.file_path points to local file for MVP)
                # This could block, so we run file io in thread
                def _process_file(file_path: str, file_type: str):
                    texts_by_page = []
                    results_to_insert = []
                    
                    if file_type == 'application/pdf':
                        # Use PyMuPDF to extract images
                        pdf_document = fitz.open(file_path)
                        for page_num in range(len(pdf_document)):
                            page = pdf_document.load_page(page_num)
                            pix = page.get_pixmap(dpi=150)
                            # Convert to numpy array for PaddleOCR
                            img_data = pix.tobytes("ppm")
                            img = Image.open(io.BytesIO(img_data)).convert('RGB')
                            img_np = np.array(img)
                            
                            # Run OCR
                            ocr_result = ocr_engine.ocr(img_np, cls=True)
                            
                            page_text = ""
                            if ocr_result and ocr_result[0]:
                                # Extract just the text from the result
                                # ocr_result[0] is a list of [box, (text, score)]
                                lines = [line[1][0] for line in ocr_result[0]]
                                page_text = "\n".join(lines)
                            
                            texts_by_page.append(page_text)
                            results_to_insert.append({
                                'page_number': page_num + 1,
                                'raw_text': page_text
                            })
                            
                    elif 'image' in str(file_type).lower():
                        img = Image.open(file_path).convert('RGB')
                        img_np = np.array(img)
                        ocr_result = ocr_engine.ocr(img_np, cls=True)
                        page_text = ""
                        if ocr_result and ocr_result[0]:
                            lines = [line[1][0] for line in ocr_result[0]]
                            page_text = "\n".join(lines)
                            
                        texts_by_page.append(page_text)
                        results_to_insert.append({
                            'page_number': 1,
                            'raw_text': page_text
                        })
                        
                    return "\n\n".join(texts_by_page), results_to_insert

                # Run blocking PyMuPDF & PaddleOCR in threadpool
                extracted_text, results_to_insert = await asyncio.to_thread(_process_file, doc.file_path, doc.file_type)
                
                # Delete existing OCR results for this document if retrying
                await db.execute(
                    OCRResult.__table__.delete().where(OCRResult.document_id == doc.id)
                )
                
                # Insert new OCRResults
                for res in results_to_insert:
                    db.add(OCRResult(
                        claim_id=claim.id,
                        document_id=doc.id,
                        page_number=res['page_number'],
                        raw_text=res['raw_text']
                    ))
                
                doc.extracted_text = extracted_text
                doc.status = DocumentStatus.OCR_COMPLETE.value
                total_extracted += 1
                
            except Exception as e:
                logger.error(f"Failed to OCR document {doc.id}: {e}")
                doc.status = DocumentStatus.FAILED.value
                
            await db.commit()

        if total_extracted > 0:
            claim.status = ClaimStatus.OCR_COMPLETE.value
            db.add(AuditLog(
                claim_id=claim.id,
                action="OCR Completed successfully",
                entity_type="Claim",
                entity_id=claim.id
            ))
        else:
            claim.status = ClaimStatus.DOCUMENT_UPLOADED.value
            
        await db.commit()
            
    except Exception as e:
        logger.error(f"Global error in OCR task for claim {claim_id}: {e}")
        claim.status = ClaimStatus.DOCUMENT_UPLOADED.value
        await db.commit()
