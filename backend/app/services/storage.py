"""
Storage service — local disk implementation.
Saves uploaded files to the `uploads/{claim_id}/` directory.
Provides save, get, and delete operations.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings

settings = get_settings()


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}

async def save_file(file: UploadFile, claim_id: str) -> tuple[str, int]:
    """
    Save an uploaded file to disk under uploads/{claim_id}/.
    Generates a unique filename using a UUID prefix.
    Reads file in chunks to prevent memory exhaustion.
    Verifies actual file MIME type via python-magic.
    Enforces a 10MB maximum file size limit.
    Returns (file_path, file_size_bytes).
    """
    import magic

    dest_dir = settings.upload_path / claim_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    original_name = Path(file.filename or "upload.bin").name
    unique_prefix = uuid.uuid4().hex[:8]
    safe_name = f"{unique_prefix}_{original_name}"
    dest = dest_dir / safe_name

    total_size = 0
    mime_checker = magic.Magic(mime=True)
    detected_mime = None

    with open(dest, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            
            if total_size == 0:
                # Check magic bytes on first chunk
                detected_mime = mime_checker.from_buffer(chunk)
                if detected_mime not in ALLOWED_MIME_TYPES:
                    f.close()
                    dest.unlink()
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid file type. Detected {detected_mime}. Allowed: PDF, JPG, PNG."
                    )
            
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                f.close()
                dest.unlink()
                raise HTTPException(status_code=413, detail="File too large. Max size is 10MB.")
                
            f.write(chunk)

    return str(dest), total_size


def get_file(file_path: str) -> Path:
    """
    Return the Path to a stored file. Raises 404 if file doesn't exist.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return p


def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk. Returns True if deleted, False if not found.
    """
    p = Path(file_path)
    if p.exists() and p.is_file():
        p.unlink()
        # Clean up empty claim directory
        parent = p.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        return True
    return False


# Legacy alias for backward compatibility
async def save_upload(file: UploadFile, claim_id: str) -> tuple[str, int]:
    """Alias for save_file — maintains backward compatibility."""
    return await save_file(file, claim_id)
