import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.database.database import get_db
from app.models import User

settings = get_settings()
security = HTTPBearer()

def verify_token(token: str) -> dict:
    if settings.auth_mock:
        return {"sub": "mock_user_id"}
    
    if not settings.clerk_issuer_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk issuer URL not configured"
        )
    
    try:
        jwks_client = jwt.PyJWKClient(f"{settings.clerk_issuer_url}/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer_url,
            options={"verify_aud": False}
        )
        return data
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    clerk_id = payload.get("sub")
    
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalars().first()
    
    if not user:
        if settings.auth_mock:
            # Create a mock user if it doesn't exist for easier dev
            user = User(clerk_id=clerk_id, email="mock@example.com", name="Mock User", organization_id="mock_org")
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            raise HTTPException(status_code=401, detail="User not found")
            
    return user
