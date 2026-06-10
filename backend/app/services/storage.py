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


async def save_file(file: UploadFile, claim_id: str) -> tuple[str, int]:
    """
    Save an uploaded file to disk under uploads/{claim_id}/.
    Generates a unique filename using a UUID prefix.
    Returns (file_path, file_size_bytes).
    """
    dest_dir = settings.upload_path / claim_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename: {uuid_prefix}_{original_name}
    original_name = Path(file.filename or "upload.bin").name
    unique_prefix = uuid.uuid4().hex[:8]
    safe_name = f"{unique_prefix}_{original_name}"
    dest = dest_dir / safe_name

    content = await file.read()
    dest.write_bytes(content)

    return str(dest), len(content)


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
