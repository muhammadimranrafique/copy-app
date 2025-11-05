from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from models import User
from config import get_settings
from uuid import UUID

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer()

"""
Use sha256_crypt as a fallback/default for environments where bcrypt
is not available or has compatibility issues. sha256_crypt is a
pure-Python implementation provided by passlib and will work without
extra binary dependencies. bcrypt is left in the schemes list so
existing hashes using bcrypt will still verify.
"""
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Token validation error: {e}")
        raise credentials_exception
    
    # Get session from generator
    from database import engine
    with Session(engine) as session:
        try:
            statement = select(User).where(User.id == UUID(user_id))
            user = session.exec(statement).first()
            
            if user is None:
                raise credentials_exception
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            return user
        except Exception as e:
            print(f"Database error in get_current_user: {e}")
            raise credentials_exception

def get_current_user_from_bearer(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """Get current user from Bearer token (alternative method for Swagger UI)."""
    return get_current_user(credentials.credentials)

