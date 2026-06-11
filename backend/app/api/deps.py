import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.farmer import Farmer
from app.repositories.farmer import farmer_repo
from app.schemas.auth import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_farmer(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> Farmer:
    """Dependency resolver verifying JWT tokens and returning the logged-in Farmer."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials token."
            )
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials token."
        )
        
    farmer = farmer_repo.get_by_id(db, farmer_id=int(token_data.sub))
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer account not found."
        )
    return farmer
