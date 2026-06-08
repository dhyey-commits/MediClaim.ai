"""
Storage service — local disk implementation.
Saves uploaded files to the `uploads/` directory.
Swap `save_file` for an S3 implementation when credentials are available.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


async def save_upload(file: UploadFile, claim_id: str) -> tuple[str, int]:
    """
    Save an uploaded file to disk.
    Returns (file_path, file_size_bytes).
    """
    dest_dir = settings.upload_path / claim_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Sanitise filename
    safe_name = Path(file.filename or "upload.bin").name
    dest = dest_dir / safe_name

    # Handle name collisions
    counter = 1
    while dest.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    content = await file.read()
    dest.write_bytes(content)

    return str(dest), len(content)


def file_url(file_path: str) -> str:
    """Return a URL-safe path for serving the file via the /files endpoint."""
    return f"/api/v1/files/{Path(file_path).relative_to(settings.upload_path).as_posix()}"
