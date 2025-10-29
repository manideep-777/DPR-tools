"""
Pydantic models for DPR form endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FormCreateRequest(BaseModel):
    """Request model for creating a new DPR form"""
    business_name: str = Field(..., min_length=1, max_length=255, description="Name of the business/project")
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "ABC Manufacturing Unit"
            }
        }


class FormCreateResponse(BaseModel):
    """Response model for successful form creation"""
    success: bool
    message: str
    form_id: int
    business_name: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FormResponse(BaseModel):
    """Response model for form data"""
    id: int
    user_id: int
    business_name: str
    status: str
    completion_percentage: int
    created_at: datetime
    last_modified: datetime
    
    class Config:
        from_attributes = True
