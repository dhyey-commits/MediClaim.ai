import sys
from pathlib import Path
sys.path.insert(0, str(Path("d:/Mediclaim-Clean/backend").resolve()))

from app.main import app

for route in app.routes:
    if "upload" in getattr(route, "path", ""):
        print(f"[{route.methods}] {route.path}")
