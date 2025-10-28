from fastapi import APIRouter, HTTPException, Depends
from app.models import UserResponse, DashboardStats
from app.routers.auth import oauth2_scheme
from app.utils.security import verify_token
from app.database import prisma

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user profile"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await prisma.user.find_unique(where={"id": payload.get("user_id")})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        organization=user.organization,
        is_active=user.is_active,
        role=user.role,
        created_at=user.created_at
    )


@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(token: str = Depends(oauth2_scheme)):
    """Get user dashboard statistics"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    
    # Get total DPRs
    total_dprs = await prisma.dpr.count(where={"user_id": user_id})
    
    # Get DPRs generated this month
    from datetime import datetime, timedelta
    month_ago = datetime.utcnow() - timedelta(days=30)
    dprs_this_month = await prisma.dpr.count(
        where={
            "user_id": user_id,
            "created_at": {"gte": month_ago}
        }
    )
    
    # Get total investment amount
    dprs = await prisma.dpr.find_many(where={"user_id": user_id})
    total_investment = sum(float(dpr.investment_amount) for dpr in dprs)
    
    # Get recent DPRs
    recent_dprs = await prisma.dpr.find_many(
        where={"user_id": user_id},
        order_by={"created_at": "desc"},
        take=5
    )
    
    recent_dprs_data = [
        {
            "id": dpr.id,
            "project_name": dpr.project_name,
            "sector": dpr.sector,
            "investment_amount": float(dpr.investment_amount),
            "status": dpr.status,
            "created_at": dpr.created_at
        }
        for dpr in recent_dprs
    ]
    
    return DashboardStats(
        total_dprs=total_dprs,
        dprs_this_month=dprs_this_month,
        total_investment=total_investment,
        recent_dprs=recent_dprs_data
    )


@router.put("/me")
async def update_profile(
    full_name: str = None,
    organization: str = None,
    token: str = Depends(oauth2_scheme)
):
    """Update user profile"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    update_data = {}
    if full_name:
        update_data["full_name"] = full_name
    if organization:
        update_data["organization"] = organization
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    user = await prisma.user.update(
        where={"id": payload.get("user_id")},
        data=update_data
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        organization=user.organization,
        is_active=user.is_active,
        role=user.role,
        created_at=user.created_at
    )
