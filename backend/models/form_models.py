"""
Pydantic models for DPR form endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


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


class FormUpdateRequest(BaseModel):
    """Request model for updating entire DPR form"""
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(draft|generating|completed)$")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["draft", "generating", "completed"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Updated Business Name",
                "status": "draft"
            }
        }


class FormUpdateResponse(BaseModel):
    """Response model for successful form update"""
    success: bool
    message: str
    form_id: int
    business_name: str
    status: str
    completion_percentage: int
    last_modified: datetime
    
    class Config:
        from_attributes = True


# Section-specific update models

class EntrepreneurDetailsUpdate(BaseModel):
    """Update model for Entrepreneur Details section"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    education: Optional[str] = Field(None, min_length=1)
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    previous_business_experience: Optional[str] = None
    technical_skills: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "date_of_birth": "1990-01-15",
                "education": "MBA",
                "years_of_experience": 5
            }
        }


class BusinessDetailsUpdate(BaseModel):
    """Update model for Business Details section"""
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, min_length=1)
    sub_sector: Optional[str] = None
    legal_structure: Optional[str] = Field(None, pattern="^(proprietorship|partnership|LLP|Pvt Ltd)$")
    registration_number: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1)
    address: Optional[str] = Field(None, min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "ABC Manufacturing",
                "sector": "Manufacturing",
                "legal_structure": "Pvt Ltd",
                "location": "Hyderabad"
            }
        }


class ProductDetailsUpdate(BaseModel):
    """Update model for Product Details section"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    key_features: Optional[List[str]] = None
    target_customers: Optional[str] = Field(None, min_length=1)
    current_capacity: Optional[int] = Field(None, ge=0)
    planned_capacity: Optional[int] = Field(None, ge=0)
    unique_selling_points: Optional[str] = Field(None, min_length=1)
    quality_certifications: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Widget Pro",
                "description": "Advanced widget manufacturing",
                "key_features": ["Durable", "Eco-friendly", "Cost-effective"],
                "planned_capacity": 10000
            }
        }


class FinancialDetailsUpdate(BaseModel):
    """Update model for Financial Details section"""
    total_investment_amount: Optional[Decimal] = Field(None, ge=0)
    land_cost: Optional[Decimal] = Field(None, ge=0)
    building_cost: Optional[Decimal] = Field(None, ge=0)
    machinery_cost: Optional[Decimal] = Field(None, ge=0)
    working_capital: Optional[Decimal] = Field(None, ge=0)
    other_costs: Optional[Decimal] = Field(None, ge=0)
    own_contribution: Optional[Decimal] = Field(None, ge=0)
    loan_required: Optional[Decimal] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_investment_amount": 5000000,
                "machinery_cost": 2000000,
                "working_capital": 1000000
            }
        }


class RevenueAssumptionsUpdate(BaseModel):
    """Update model for Revenue Assumptions section"""
    product_price: Optional[Decimal] = Field(None, ge=0)
    monthly_sales_quantity_year1: Optional[int] = Field(None, ge=0)
    monthly_sales_quantity_year2: Optional[int] = Field(None, ge=0)
    monthly_sales_quantity_year3: Optional[int] = Field(None, ge=0)
    growth_rate_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_price": 500,
                "monthly_sales_quantity_year1": 1000,
                "growth_rate_percentage": 15
            }
        }


class CostDetailsUpdate(BaseModel):
    """Update model for Cost Details section"""
    raw_material_cost_monthly: Optional[Decimal] = Field(None, ge=0)
    labor_cost_monthly: Optional[Decimal] = Field(None, ge=0)
    utilities_cost_monthly: Optional[Decimal] = Field(None, ge=0)
    rent_monthly: Optional[Decimal] = Field(None, ge=0)
    marketing_cost_monthly: Optional[Decimal] = Field(None, ge=0)
    other_fixed_costs_monthly: Optional[Decimal] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_material_cost_monthly": 50000,
                "labor_cost_monthly": 30000,
                "utilities_cost_monthly": 10000
            }
        }


class StaffingDetailsUpdate(BaseModel):
    """Update model for Staffing Details section"""
    total_employees: Optional[int] = Field(None, ge=1)
    management_count: Optional[int] = Field(None, ge=0)
    technical_staff_count: Optional[int] = Field(None, ge=0)
    support_staff_count: Optional[int] = Field(None, ge=0)
    average_salary: Optional[Decimal] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_employees": 25,
                "management_count": 3,
                "technical_staff_count": 15
            }
        }


class TimelineDetailsUpdate(BaseModel):
    """Update model for Timeline Details section"""
    land_acquisition_months: Optional[int] = Field(None, ge=0, le=60)
    construction_months: Optional[int] = Field(None, ge=0, le=60)
    machinery_installation_months: Optional[int] = Field(None, ge=0, le=60)
    trial_production_months: Optional[int] = Field(None, ge=0, le=60)
    commercial_production_start_month: Optional[int] = Field(None, ge=0, le=120)
    
    class Config:
        json_schema_extra = {
            "example": {
                "land_acquisition_months": 2,
                "construction_months": 6,
                "machinery_installation_months": 3
            }
        }


class SectionUpdateResponse(BaseModel):
    """Response model for section update operations"""
    success: bool
    message: str
    form_id: int
    section_name: str
    completion_percentage: int
    last_modified: datetime
    
    class Config:
        from_attributes = True


# Complete form retrieval models

class EntrepreneurDetailsResponse(BaseModel):
    """Response model for Entrepreneur Details"""
    full_name: str
    date_of_birth: date
    education: str
    years_of_experience: int
    previous_business_experience: Optional[str] = None
    technical_skills: Optional[str] = None
    
    class Config:
        from_attributes = True


class BusinessDetailsResponse(BaseModel):
    """Response model for Business Details"""
    business_name: str
    sector: str
    sub_sector: Optional[str] = None
    legal_structure: str
    registration_number: Optional[str] = None
    location: str
    address: str
    
    class Config:
        from_attributes = True


class ProductDetailsResponse(BaseModel):
    """Response model for Product Details"""
    product_name: str
    description: str
    key_features: List[str]
    target_customers: str
    current_capacity: Optional[int] = None
    planned_capacity: int
    unique_selling_points: str
    quality_certifications: Optional[str] = None
    
    class Config:
        from_attributes = True


class FinancialDetailsResponse(BaseModel):
    """Response model for Financial Details"""
    total_investment_amount: Decimal
    land_cost: Decimal
    building_cost: Decimal
    machinery_cost: Decimal
    working_capital: Decimal
    other_costs: Decimal
    own_contribution: Decimal
    loan_required: Decimal
    
    class Config:
        from_attributes = True


class RevenueAssumptionsResponse(BaseModel):
    """Response model for Revenue Assumptions"""
    product_price: Decimal
    monthly_sales_quantity_year1: int
    monthly_sales_quantity_year2: int
    monthly_sales_quantity_year3: int
    growth_rate_percentage: Decimal
    
    class Config:
        from_attributes = True


class CostDetailsResponse(BaseModel):
    """Response model for Cost Details"""
    raw_material_cost_monthly: Decimal
    labor_cost_monthly: Decimal
    utilities_cost_monthly: Decimal
    rent_monthly: Decimal
    marketing_cost_monthly: Decimal
    other_fixed_costs_monthly: Decimal
    
    class Config:
        from_attributes = True


class StaffingDetailsResponse(BaseModel):
    """Response model for Staffing Details"""
    total_employees: int
    management_count: int
    technical_staff_count: int
    support_staff_count: int
    average_salary: Decimal
    
    class Config:
        from_attributes = True


class TimelineDetailsResponse(BaseModel):
    """Response model for Timeline Details"""
    land_acquisition_months: int
    construction_months: int
    machinery_installation_months: int
    trial_production_months: int
    commercial_production_start_month: int
    
    class Config:
        from_attributes = True


class CompleteFormResponse(BaseModel):
    """Response model for complete form data with all sections"""
    # Main form data
    id: int
    user_id: int
    business_name: str
    status: str
    completion_percentage: int
    created_at: datetime
    last_modified: datetime
    
    # All sections (optional - only included if they exist)
    entrepreneur_details: Optional[EntrepreneurDetailsResponse] = None
    business_details: Optional[BusinessDetailsResponse] = None
    product_details: Optional[ProductDetailsResponse] = None
    financial_details: Optional[FinancialDetailsResponse] = None
    revenue_assumptions: Optional[RevenueAssumptionsResponse] = None
    cost_details: Optional[CostDetailsResponse] = None
    staffing_details: Optional[StaffingDetailsResponse] = None
    timeline_details: Optional[TimelineDetailsResponse] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "business_name": "ABC Manufacturing",
                "status": "draft",
                "completion_percentage": 75,
                "created_at": "2025-10-29T00:00:00",
                "last_modified": "2025-10-29T12:00:00",
                "entrepreneur_details": {
                    "full_name": "John Doe",
                    "date_of_birth": "1990-01-15",
                    "education": "MBA",
                    "years_of_experience": 8
                },
                "business_details": {
                    "business_name": "ABC Corp",
                    "sector": "Manufacturing",
                    "legal_structure": "Pvt Ltd",
                    "location": "Hyderabad",
                    "address": "123 Street"
                }
            }
        }


class FormListItem(BaseModel):
    """Response model for form list item"""
    id: int
    business_name: str
    status: str
    completion_percentage: int
    created_at: datetime
    last_modified: datetime
    
    class Config:
        from_attributes = True


class UserFormsResponse(BaseModel):
    """Response model for user's forms list"""
    total_forms: int
    forms: List[FormListItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_forms": 3,
                "forms": [
                    {
                        "id": 1,
                        "business_name": "ABC Manufacturing",
                        "status": "completed",
                        "completion_percentage": 100,
                        "created_at": "2025-10-29T00:00:00",
                        "last_modified": "2025-10-29T12:00:00"
                    },
                    {
                        "id": 2,
                        "business_name": "XYZ Services",
                        "status": "draft",
                        "completion_percentage": 45,
                        "created_at": "2025-10-28T00:00:00",
                        "last_modified": "2025-10-28T15:00:00"
                    }
                ]
            }
        }
