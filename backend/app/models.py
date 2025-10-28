from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# ==================== USER MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ==================== DPR MODELS (ENHANCED) ====================

class DPRCreate(BaseModel):
    # Basic Information
    project_name: str
    sector: str
    subsector: Optional[str] = None
    location: str
    investment_amount: float
    loan_amount: Optional[float] = None
    employment: Optional[int] = None
    
    # Cluster-Specific
    cluster_name: Optional[str] = None
    number_of_units: Optional[int] = None
    number_of_workers: Optional[int] = None
    spv_name: Optional[str] = None
    diagnostic_agency: Optional[str] = None
    
    # Project Details
    project_description: str
    products_services: Optional[Dict[str, Any]] = None
    
    # SWOT Analysis
    swot_analysis: Optional[Dict[str, List[str]]] = None  # {strengths: [], weaknesses: [], opportunities: [], threats: []}
    
    # Interventions
    hard_interventions: Optional[List[Dict[str, Any]]] = None
    soft_interventions: Optional[List[Dict[str, Any]]] = None
    
    # Financial
    grant_percentage: Optional[float] = None
    project_duration_months: Optional[int] = 36  # Default 3 years
    
    # Implementation
    implementation_timeline: Optional[List[Dict[str, Any]]] = None
    
    # KPIs
    kpis: Optional[List[Dict[str, Any]]] = None
    
    # Sustainability
    sustainability_plan: Optional[Dict[str, Any]] = None


class DPRUpdate(BaseModel):
    project_name: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    investment_amount: Optional[float] = None
    project_description: Optional[str] = None
    swot_analysis: Optional[Dict[str, List[str]]] = None
    hard_interventions: Optional[List[Dict[str, Any]]] = None
    soft_interventions: Optional[List[Dict[str, Any]]] = None
    financial_projections: Optional[Dict[str, Any]] = None


class DPRResponse(BaseModel):
    id: int
    project_name: str
    sector: str
    location: str
    investment_amount: float
    status: str
    created_at: datetime
    pdf_path: Optional[str] = None
    cluster_name: Optional[str] = None
    number_of_units: Optional[int] = None
    government_grant: Optional[float] = None
    beneficiary_contribution: Optional[float] = None


class FinancialProjection(BaseModel):
    revenue_projections: List[float]
    operating_expenses: List[float]
    profit_projections: List[float]
    break_even_period: str
    roi_percentage: str


# ==================== DASHBOARD MODELS ====================

class DashboardStats(BaseModel):
    total_dprs: int
    total_investment: float
    recent_dprs: List[DPRResponse]
