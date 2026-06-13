import re
from pathlib import Path

def process_file(filepath):
    path = Path(filepath)
    content = path.read_text(encoding='utf-8')
    
    # Add imports if not present
    if "from app.core.security import get_current_user" not in content:
        content = content.replace("from app.models import", "from app.core.security import get_current_user\nfrom app.models import")
    if "User" not in content and "from app.models import" in content:
        # User is already exported in models/__init__.py
        content = content.replace("from app.models import ", "from app.models import User, ")
    
    # 1. Add current_user to dependencies
    # We look for: db: AsyncSession = Depends(get_db)
    # or db: AsyncSession = Depends(get_db),
    # and add current_user: User = Depends(get_current_user),
    pattern_db = re.compile(r'(db:\s*AsyncSession\s*=\s*Depends\(get_db\),?)')
    
    def repl_db(match):
        text = match.group(1)
        if not text.endswith(','):
            text += ','
        # Don't add if current_user is already in the function signature
        return text + '\n    current_user: User = Depends(get_current_user),'

    # Actually, replacing all db: AsyncSession with db + current_user is risky if it replaces multiple times per function.
    # We can split by 'async def '
    parts = content.split('async def ')
    for i in range(1, len(parts)):
        if "current_user: User" not in parts[i] and "db: AsyncSession = Depends(get_db)" in parts[i]:
            parts[i] = pattern_db.sub(repl_db, parts[i], count=1)
            
            # Replace Claim.id == claim_id with the authorization check
            parts[i] = parts[i].replace("Claim.id == claim_id)", "Claim.id == claim_id, Claim.organization_id == current_user.organization_id)")
            parts[i] = parts[i].replace("Claim.id == claim_id\n", "Claim.id == claim_id, Claim.organization_id == current_user.organization_id\n")

            # Also replace ClaimICDRecommendation lookups if they exist, but maybe that's fine since we verify claim_id right after.
            # E.g., `if not rec or rec.claim_id != claim_id:` and then the claim is already filtered by org.
            
    new_content = 'async def '.join(parts)
    
    # For create_claim, we need to set organization_id
    new_content = new_content.replace(
        'created_by_id="system",  # TODO: get from auth',
        'created_by_id=current_user.id,\n        organization_id=current_user.organization_id,'
    )
    
    path.write_text(new_content, encoding='utf-8')

for f in ['d:/Mediclaim-Clean/backend/app/api/claims.py', 'd:/Mediclaim-Clean/backend/app/api/documents.py', 'd:/Mediclaim-Clean/backend/app/api/reports.py']:
    if Path(f).exists():
        process_file(f)
        print(f"Processed {f}")

