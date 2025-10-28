from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import UserCreate, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, verify_token
from app.database import prisma
from datetime import timedelta
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await prisma.user.find_first(
        where={
            "OR": [
                {"email": user.email},
                {"username": user.username}
            ]
        }
    )
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = await prisma.user.create(
        data={
            "email": user.email,
            "username": user.username,
            "password_hash": hashed_password,
            "full_name": user.full_name,
            "phone": user.phone,
        }
    )
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        full_name=new_user.full_name,
        phone=new_user.phone,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return JWT token"""
    # Find user by username
    user = await prisma.user.find_first(
        where={"username": form_data.username}
    )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    user = await prisma.user.find_unique(where={"id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/verify")
async def verify_user_token(token: str = Depends(oauth2_scheme)):
    """Verify if token is valid"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"valid": True, "user_id": payload.get("user_id")}
