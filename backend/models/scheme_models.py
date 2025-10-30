"""
Pydantic models for Government Schemes
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class SchemeBase(BaseModel):
    """Base schema for government scheme"""
    scheme_name: str = Field(..., description="Name of the government scheme")
    ministry: str = Field(..., description="Ministry offering the scheme")
    scheme_type: str = Field(..., description="Type: subsidy, loan, training, etc.")
    description: str = Field(..., description="Detailed description of the scheme")
    subsidy_percentage: Optional[Decimal] = Field(None, description="Subsidy percentage if applicable")
    max_subsidy_amount: Optional[Decimal] = Field(None, description="Maximum subsidy amount")
    eligible_sectors: List[str] = Field(..., description="List of eligible business sectors")
    eligible_states: List[str] = Field(..., description="List of eligible states")
    min_investment: Optional[Decimal] = Field(None, description="Minimum investment required")
    max_investment: Optional[Decimal] = Field(None, description="Maximum investment allowed")
    eligibility_criteria: str = Field(..., description="Detailed eligibility criteria")
    application_link: Optional[str] = Field(None, description="Link to apply for the scheme")


class SchemeResponse(SchemeBase):
    """Schema for government scheme response"""
    id: int
    match_score: Optional[int] = Field(None, description="Matching score (0-100)")
    match_reasons: Optional[List[str]] = Field(None, description="Reasons for matching")
    key_benefit: Optional[str] = Field(None, description="AI-generated key benefit highlight")

    class Config:
        from_attributes = True


class SchemeMatchRequest(BaseModel):
    """Request for matching schemes"""
    max_results: Optional[int] = Field(10, description="Maximum number of results to return", ge=1, le=50)


class SchemeMatchResponse(BaseModel):
    """Response for matched schemes"""
    success: bool
    form_id: int
    business_name: str
    total_matches: int
    matched_schemes: List[SchemeResponse]
    message: str
