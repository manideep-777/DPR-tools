"""
Authentication routes for MSME DPR Generator
Handles user registration, login, and token management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from prisma import Prisma
from datetime import datetime
import logging

from models.auth_models import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    ErrorResponse
)
from utils.auth_utils import hash_password, verify_password, create_access_token
from middleware.auth import get_current_user, CurrentUser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Prisma client instance
prisma = Prisma()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, password, and business details"
)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **password**: Strong password (min 8 chars, 1 upper, 1 lower, 1 digit)
    - **full_name**: User's full name
    - **phone**: Phone number (10+ digits)
    - **business_type**: Type of business (optional)
    - **state**: User's state (optional)
    
    Returns:
    - User ID and email on success
    - Error message on failure
    """
    try:
        # Connect to database
        if not prisma.is_connected():
            await prisma.connect()
        
        # Check if email already exists
        existing_user = await prisma.user.find_unique(
            where={"email": user_data.email}
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create the user
        new_user = await prisma.user.create(
            data={
                "email": user_data.email,
                "hashedPassword": hashed_password,
                "fullName": user_data.fullName,
                "phone": user_data.phone,
                "businessType": user_data.businessType,
                "state": user_data.state,
                "lastLogin": datetime.utcnow()
            }
        )
        
        logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
        
        return UserRegisterResponse(
            success=True,
            message="User registered successfully",
            user_id=new_user.id,
            email=new_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User login",
    description="Authenticate user and receive JWT access token"
)
async def login_user(credentials: UserLoginRequest):
    """
    Authenticate user and generate access token
    
    - **email**: Registered email address
    - **password**: User's password
    
    Returns:
    - JWT access token
    - User profile information
    """
    try:
        # Connect to database
        if not prisma.is_connected():
            await prisma.connect()
        
        # Find user by email
        user = await prisma.user.find_unique(
            where={"email": credentials.email}
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashedPassword):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        await prisma.user.update(
            where={"id": user.id},
            data={"lastLogin": datetime.utcnow()}
        )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        logger.info(f"User logged in: {user.email} (ID: {user.id})")
        
        return UserLoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.fullName,
                "business_type": user.businessType,
                "state": user.state
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if authentication service is running"
)
async def health_check():
    """Health check endpoint for authentication service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/me",
    summary="Get current user",
    description="Get the current authenticated user's information"
)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Protected endpoint - requires valid JWT token
    Returns the current user's profile information
    
    This endpoint demonstrates the JWT authentication middleware
    """
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "business_type": current_user.business_type,
            "state": current_user.state
        }
    }
