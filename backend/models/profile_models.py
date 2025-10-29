"""
Pydantic models for user profile endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserProfileResponse(BaseModel):
    """Response model for user profile data"""
    id: int
    user_id: int
    address: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    years_in_business: Optional[int] = None
    bio: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    address: Optional[str] = Field(None, max_length=500)
    aadhar_number: Optional[str] = Field(None, pattern=r'^\d{12}$')
    pan_number: Optional[str] = Field(None, pattern=r'^[A-Z]{5}\d{4}[A-Z]$')
    years_in_business: Optional[int] = Field(None, ge=0, le=100)
    bio: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('aadhar_number')
    @classmethod
    def validate_aadhar(cls, v: Optional[str]) -> Optional[str]:
        """Validate Aadhar number is exactly 12 digits"""
        if v is not None and (not v.isdigit() or len(v) != 12):
            raise ValueError('Aadhar number must be exactly 12 digits')
        return v
    
    @field_validator('pan_number')
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        """Validate PAN number format (5 letters, 4 digits, 1 letter)"""
        if v is not None:
            v = v.upper()
            if not (len(v) == 10 and 
                    v[:5].isalpha() and 
                    v[5:9].isdigit() and 
                    v[9].isalpha()):
                raise ValueError('PAN number must follow format: ABCDE1234F')
        return v


class ProfileUpdateResponse(BaseModel):
    """Response model for successful profile update"""
    success: bool
    message: str
    profile: UserProfileResponse
