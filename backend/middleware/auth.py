"""
JWT Authentication Middleware for MSME DPR Generator
Provides dependency injection for protected routes
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from prisma import Prisma
from utils.auth_utils import decode_access_token
import logging

# Setup logging
logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()

# Prisma client
prisma = Prisma()


class CurrentUser:
    """
    User information extracted from JWT token
    """
    def __init__(self, user_id: int, email: str, user_data: dict):
        self.id = user_id
        self.email = email
        self.full_name = user_data.get("fullName")
        self.phone = user_data.get("phone")
        self.business_type = user_data.get("businessType")
        self.state = user_data.get("state")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user from JWT token
    
    This middleware:
    1. Extracts JWT token from Authorization header
    2. Verifies token signature and expiry
    3. Retrieves user from database
    4. Returns CurrentUser object for use in route handlers
    
    Args:
        credentials: HTTPAuthorizationCredentials from HTTPBearer
        
    Returns:
        CurrentUser object with user information
        
    Raises:
        HTTPException: 401 if token is invalid, expired, or user not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    if not token:
        logger.warning("No token provided in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode and verify token
    payload = decode_access_token(token)
    
    if payload is None:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user information from token
    email: Optional[str] = payload.get("sub")
    user_id: Optional[int] = payload.get("user_id")
    
    if email is None or user_id is None:
        logger.error("Token missing required claims (sub or user_id)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Connect to database if not connected
    if not prisma.is_connected():
        await prisma.connect()
    
    # Retrieve user from database
    try:
        user = await prisma.user.find_unique(
            where={"id": user_id}
        )
        
        if user is None:
            logger.warning(f"User not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify email matches
        if user.email != email:
            logger.warning(f"Email mismatch for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create CurrentUser object
        current_user = CurrentUser(
            user_id=user.id,
            email=user.email,
            user_data={
                "fullName": user.fullName,
                "phone": user.phone,
                "businessType": user.businessType,
                "state": user.state
            }
        )
        
        logger.info(f"User authenticated: {user.email} (ID: {user.id})")
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user from database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """
    Optional dependency to get current user if token is provided
    
    Use this for routes that can work with or without authentication
    
    Args:
        credentials: Optional HTTPAuthorizationCredentials
        
    Returns:
        CurrentUser object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
