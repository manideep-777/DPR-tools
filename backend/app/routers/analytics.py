from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import oauth2_scheme
from app.utils.security import verify_token
from app.database import prisma
from typing import List, Dict

router = APIRouter()


@router.get("/sectors")
async def get_sector_statistics(token: str = Depends(oauth2_scheme)):
    """Get statistics by sector"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get all DPRs
    dprs = await prisma.dpr.find_many()
    
    # Group by sector
    sector_stats = {}
    for dpr in dprs:
        sector = dpr.sector
        if sector not in sector_stats:
            sector_stats[sector] = {
                "sector": sector,
                "count": 0,
                "total_investment": 0.0,
                "avg_investment": 0.0,
                "total_employment": 0
            }
        
        sector_stats[sector]["count"] += 1
        sector_stats[sector]["total_investment"] += float(dpr.investment_amount)
        if dpr.employment:
            sector_stats[sector]["total_employment"] += dpr.employment
    
    # Calculate averages
    for sector in sector_stats:
        count = sector_stats[sector]["count"]
        sector_stats[sector]["avg_investment"] = sector_stats[sector]["total_investment"] / count
    
    return list(sector_stats.values())


@router.get("/platform-stats")
async def get_platform_statistics(token: str = Depends(oauth2_scheme)):
    """Get overall platform statistics (admin only)"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if admin
    user = await prisma.user.find_unique(where={"id": payload.get("user_id")})
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total users
    total_users = await prisma.user.count()
    
    # Total DPRs
    total_dprs = await prisma.dpr.count()
    
    # Total investment
    dprs = await prisma.dpr.find_many()
    total_investment = sum(float(dpr.investment_amount) for dpr in dprs)
    
    # Total employment
    total_employment = sum(dpr.employment for dpr in dprs if dpr.employment)
    
    # Average investment
    avg_investment = total_investment / total_dprs if total_dprs > 0 else 0
    
    # DPRs by status
    draft_count = await prisma.dpr.count(where={"status": "DRAFT"})
    generated_count = await prisma.dpr.count(where={"status": "GENERATED"})
    
    return {
        "total_users": total_users,
        "total_dprs": total_dprs,
        "total_investment": total_investment,
        "total_employment": total_employment,
        "avg_investment": avg_investment,
        "dprs_by_status": {
            "draft": draft_count,
            "generated": generated_count
        }
    }


@router.get("/benchmarks")
async def get_sector_benchmarks(sector: str = None, token: str = Depends(oauth2_scheme)):
    """Get sector benchmarks for comparison"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    where_clause = {"sector": sector} if sector else {}
    dprs = await prisma.dpr.find_many(where=where_clause)
    
    if not dprs:
        raise HTTPException(status_code=404, detail="No data found for the sector")
    
    # Calculate benchmarks
    investments = [float(dpr.investment_amount) for dpr in dprs]
    employments = [dpr.employment for dpr in dprs if dpr.employment]
    
    npvs = [float(dpr.npv) for dpr in dprs if dpr.npv]
    irrs = [float(dpr.irr) for dpr in dprs if dpr.irr]
    
    def calculate_percentile(values, percentile):
        if not values:
            return None
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    benchmarks = {
        "sector": sector or "All Sectors",
        "sample_size": len(dprs),
        "investment": {
            "min": min(investments) if investments else None,
            "max": max(investments) if investments else None,
            "avg": sum(investments) / len(investments) if investments else None,
            "median": calculate_percentile(investments, 50),
            "p25": calculate_percentile(investments, 25),
            "p75": calculate_percentile(investments, 75)
        },
        "employment": {
            "min": min(employments) if employments else None,
            "max": max(employments) if employments else None,
            "avg": sum(employments) / len(employments) if employments else None,
            "median": calculate_percentile(employments, 50)
        },
        "npv": {
            "avg": sum(npvs) / len(npvs) if npvs else None,
            "median": calculate_percentile(npvs, 50)
        },
        "irr": {
            "avg": sum(irrs) / len(irrs) if irrs else None,
            "median": calculate_percentile(irrs, 50)
        }
    }
    
    return benchmarks
