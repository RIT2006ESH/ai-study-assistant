from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Changed to auto_error=False for testing

# ==================== TESTING MODE ====================
# Set to True to bypass authentication during development
TESTING_MODE = True  # Change to False when you have real authentication
TEST_USER_ID = 1

# ==================== PASSWORD UTILITIES ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


# ==================== JWT TOKEN UTILITIES ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data (must include 'sub' for user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dictionary or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None


# ==================== AUTHENTICATION DEPENDENCY ====================

async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> int:
    """
    Extract and verify the current user ID from JWT token in Authorization header.
    
    In TESTING_MODE: Returns a default test user ID
    In PRODUCTION: Validates JWT token and extracts user_id
    
    Args:
        credentials: HTTP Bearer credentials from request header
    
    Returns:
        User ID string
    
    Raises:
        HTTPException: If token is invalid, expired, or missing in production mode
    """
    
    # ===== TESTING MODE =====
    if TESTING_MODE:
        print(f"[TESTING MODE] Bypassing authentication, using test user: {TEST_USER_ID}")
        return TEST_USER_ID
    
    # ===== PRODUCTION MODE =====
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Authorization header required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


# ==================== OPTIONAL AUTHENTICATION ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    Optional authentication - returns user_id if authenticated, None otherwise
    Does not raise exceptions for missing/invalid tokens
    
    Args:
        credentials: HTTP Bearer credentials from request header
    
    Returns:
        User ID string if authenticated, None otherwise
    """
    if TESTING_MODE:
        return TEST_USER_ID
    
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    return payload.get("sub")


# ==================== ADMIN CHECK ====================

async def get_current_admin_user(
    user_id: str = Depends(get_current_user_id)
) -> str:
    """
    Verify that the current user is an admin
    
    TODO: Implement actual admin check against database
    
    Args:
        user_id: Current authenticated user ID
    
    Returns:
        User ID if admin
    
    Raises:
        HTTPException: If user is not an admin
    """
    # TODO: Check if user is admin in database
    # For now, allow all users in testing mode
    if TESTING_MODE:
        return user_id
    
    # In production, check database for admin role
    # if not db.query(User).filter(User.id == user_id, User.is_admin == True).first():
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_id