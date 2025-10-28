"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============================================
# Authentication Models
# ============================================

class UserRegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    fullName: str = Field(..., min_length=2, max_length=100, alias="full_name")
    phone: str = Field(..., min_length=10, max_length=15)
    businessType: Optional[str] = Field(None, alias="business_type")
    state: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @validator('phone')
    def phone_validation(cls, v):
        """Validate phone number format"""
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return digits
    
    class Config:
        populate_by_name = True


class UserRegisterResponse(BaseModel):
    """Response model for user registration"""
    success: bool
    message: str
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Response model for user login"""
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[dict] = None


class TokenData(BaseModel):
    """Model for decoded token data"""
    email: Optional[str] = None
    user_id: Optional[int] = None


# ============================================
# User Models
# ============================================

class UserProfile(BaseModel):
    """User profile response model"""
    id: int
    email: str
    fullName: str = Field(..., alias="full_name")
    phone: str
    businessType: Optional[str] = Field(None, alias="business_type")
    state: Optional[str] = None
    createdAt: datetime = Field(..., alias="created_at")
    lastLogin: Optional[datetime] = Field(None, alias="last_login")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ============================================
# Error Models
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
