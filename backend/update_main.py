import re

with open('app/main.py', 'r') as f:
    content = f.read()

# Add imports
imports = """
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger import get_logger
logger = get_logger(__name__)
"""
content = content.replace("from app.core.config import get_settings", imports + "\nfrom app.core.config import get_settings")

# Replace print with logger
content = content.replace('print("[MediClaim AI] API starting up...")', 'logger.info("[MediClaim AI] API starting up...")')
content = content.replace('print("[ERROR] GEMINI_API_KEY is missing from environment variables.")', 'logger.error("GEMINI_API_KEY is missing from environment variables.")')
content = content.replace('print(f"[OK] GEMINI_API_KEY loaded successfully ({settings.gemini_api_key[:8]}...)")', 'logger.info("GEMINI_API_KEY loaded successfully")')
content = content.replace('print("[OK] Database initialised (PostgreSQL)")', 'logger.info("Database initialised")')
content = content.replace('print(f"[WARN] Database init warning: {e}")', 'logger.warning(f"Database init warning: {e}")')
content = content.replace('print(f"[OK] Upload directory: {settings.upload_path}")', 'logger.info(f"Upload directory: {settings.upload_path}")')
content = content.replace('print("[MediClaim AI] API shutting down")', 'logger.info("[MediClaim AI] API shutting down")')

# Add exception handler
exception_handler = """
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
"""
content = content.replace("app.add_middleware(", exception_handler + "\napp.add_middleware(")

# Add security headers middleware
security_middleware = """
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
"""
content = content.replace("app.add_middleware(\n    CORSMiddleware,", security_middleware + "\napp.add_middleware(\n    CORSMiddleware,")

with open('app/main.py', 'w') as f:
    f.write(content)
