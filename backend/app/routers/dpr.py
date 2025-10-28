from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from app.models import DPRCreate, DPRResponse
from app.routers.auth import oauth2_scheme
from app.utils.security import verify_token
from app.utils.ai_service import (
    generate_swot_analysis,
    generate_interventions,
    generate_kpis,
    generate_market_analysis,
    generate_financial_projections,
    generate_executive_summary
)
from app.utils.pdf_generator import generate_dpr_pdf
from app.database import prisma
from pathlib import Path
from typing import List

router = APIRouter()


@router.post("/create", response_model=DPRResponse)
async def create_dpr(
    dpr_data: DPRCreate,
    token: str = Depends(oauth2_scheme)
):
    """Create a new DPR with AI-generated insights"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    
    # Prepare cluster info for AI
    cluster_info = {
        "number_of_units": dpr_data.number_of_units,
        "number_of_workers": dpr_data.number_of_workers,
        "spv_name": dpr_data.spv_name
    }
    
    # Generate AI insights if not provided
    try:
        # Generate SWOT if not provided
        if not dpr_data.swot_analysis:
            swot_analysis = await generate_swot_analysis(
                dpr_data.sector,
                dpr_data.location,
                dpr_data.project_name,
                cluster_info
            )
        else:
            swot_analysis = dpr_data.swot_analysis
        
        # Generate Interventions if not provided
        if not dpr_data.hard_interventions and not dpr_data.soft_interventions:
            interventions = await generate_interventions(
                dpr_data.sector,
                swot_analysis,
                dpr_data.investment_amount
            )
            hard_interventions = interventions.get("hard", [])
            soft_interventions = interventions.get("soft", [])
        else:
            hard_interventions = dpr_data.hard_interventions or []
            soft_interventions = dpr_data.soft_interventions or []
        
        # Generate KPIs if not provided
        if not dpr_data.kpis:
            kpis = await generate_kpis(
                dpr_data.sector,
                dpr_data.project_name,
                {"hard": hard_interventions, "soft": soft_interventions}
            )
        else:
            kpis = dpr_data.kpis
        
        # Generate Market Analysis
        market_analysis = await generate_market_analysis(
            dpr_data.sector,
            dpr_data.location,
            dpr_data.project_name
        )
        
        # Generate Financial Projections
        financial_projections = await generate_financial_projections(
            dpr_data.investment_amount,
            dpr_data.sector,
            dpr_data.employment or 10,
            dpr_data.project_duration_months or 36
        )
        
    except Exception as e:
        print(f"AI generation error: {e}")
        swot_analysis = {}
        hard_interventions = []
        soft_interventions = []
        kpis = []
        market_analysis = {}
        financial_projections = {}
    
    # Calculate financial metrics
    grant_percentage = dpr_data.grant_percentage or 70.0  # Default 70% government grant
    government_grant = float(dpr_data.investment_amount) * (grant_percentage / 100)
    beneficiary_contribution = float(dpr_data.investment_amount) - government_grant
    
    # Extract NPV and IRR from financial projections
    npv = financial_projections.get("npv", dpr_data.investment_amount * 0.35)
    irr_str = financial_projections.get("irr", "22%")
    irr = float(irr_str.replace("%", "")) if irr_str else 22.0
    break_even_str = financial_projections.get("break_even_period", "18 months")
    break_even_months = int(break_even_str.split()[0]) if "months" in break_even_str else 18
    
    # Build data dict, handling None values properly for Prisma
    create_data = {
        "user_id": user_id,
        "project_name": dpr_data.project_name,
        "sector": dpr_data.sector,
        "location": dpr_data.location,
        "investment_amount": dpr_data.investment_amount,
        "project_description": dpr_data.project_description,
        "status": "DRAFT",
        "government_grant": government_grant,
        "beneficiary_contribution": beneficiary_contribution,
        "grant_percentage": grant_percentage,
        "npv": npv,
        "irr": irr,
        "break_even_months": break_even_months,
    }
    
    # Add optional fields only if they have values
    if dpr_data.subsector:
        create_data["subsector"] = dpr_data.subsector
    if dpr_data.loan_amount is not None:
        create_data["loan_amount"] = dpr_data.loan_amount
    if dpr_data.employment is not None:
        create_data["employment"] = dpr_data.employment
    if dpr_data.cluster_name:
        create_data["cluster_name"] = dpr_data.cluster_name
    if dpr_data.number_of_units is not None:
        create_data["number_of_units"] = dpr_data.number_of_units
    if dpr_data.number_of_workers is not None:
        create_data["number_of_workers"] = dpr_data.number_of_workers
    if dpr_data.spv_name:
        create_data["spv_name"] = dpr_data.spv_name
    if dpr_data.diagnostic_agency:
        create_data["diagnostic_agency"] = dpr_data.diagnostic_agency
    if dpr_data.products_services is not None:
        create_data["products_services"] = dpr_data.products_services
    if dpr_data.project_duration_months is not None:
        create_data["project_duration_months"] = dpr_data.project_duration_months
    if swot_analysis:
        create_data["swot_analysis"] = swot_analysis
    if hard_interventions:
        create_data["hard_interventions"] = hard_interventions
    if soft_interventions:
        create_data["soft_interventions"] = soft_interventions
    if market_analysis:
        create_data["market_analysis"] = market_analysis
    if financial_projections:
        create_data["financial_projections"] = financial_projections
    if kpis:
        create_data["kpis"] = kpis
    if dpr_data.implementation_timeline:
        create_data["implementation_timeline"] = dpr_data.implementation_timeline
    if dpr_data.sustainability_plan:
        create_data["sustainability_plan"] = dpr_data.sustainability_plan
    
    dpr = await prisma.dpr.create(data=create_data)
    
    return DPRResponse(
        id=dpr.id,
        project_name=dpr.project_name,
        sector=dpr.sector,
        location=dpr.location,
        investment_amount=float(dpr.investment_amount),
        status=dpr.status,
        created_at=dpr.created_at,
        pdf_path=dpr.pdf_path,
        cluster_name=dpr.cluster_name,
        number_of_units=dpr.number_of_units,
        government_grant=float(dpr.government_grant) if dpr.government_grant else None,
        beneficiary_contribution=float(dpr.beneficiary_contribution) if dpr.beneficiary_contribution else None
    )


@router.get("/list", response_model=List[DPRResponse])
async def list_dprs(token: str = Depends(oauth2_scheme)):
    """Get all DPRs for current user"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    
    dprs = await prisma.dpr.find_many(
        where={"user_id": user_id},
        order_by={"created_at": "desc"}
    )
    
    return [
        DPRResponse(
            id=dpr.id,
            project_name=dpr.project_name,
            sector=dpr.sector,
            location=dpr.location,
            investment_amount=float(dpr.investment_amount),
            status=dpr.status,
            created_at=dpr.created_at,
            pdf_path=dpr.pdf_path,
            cluster_name=dpr.cluster_name,
            number_of_units=dpr.number_of_units,
            government_grant=float(dpr.government_grant) if dpr.government_grant else None,
            beneficiary_contribution=float(dpr.beneficiary_contribution) if dpr.beneficiary_contribution else None
        )
        for dpr in dprs
    ]


@router.get("/{dpr_id}")
async def get_dpr(dpr_id: int, token: str = Depends(oauth2_scheme)):
    """Get a specific DPR"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    dpr = await prisma.dpr.find_unique(where={"id": dpr_id})
    if not dpr:
        raise HTTPException(status_code=404, detail="DPR not found")
    
    if dpr.user_id != payload.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return dpr


@router.post("/{dpr_id}/generate-pdf")
async def generate_pdf(
    dpr_id: int,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """Generate PDF for a DPR"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    dpr = await prisma.dpr.find_unique(where={"id": dpr_id})
    if not dpr:
        raise HTTPException(status_code=404, detail="DPR not found")
    
    if dpr.user_id != payload.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Prepare PDF data
    pdf_data = {
        "project_name": dpr.project_name,
        "sector": dpr.sector,
        "location": dpr.location,
        "investment_amount": float(dpr.investment_amount),
        "market_analysis": dpr.market_analysis,
        "financial_projections": dpr.financial_projections,
        "project_description": dpr.project_description,
        "employment": dpr.employment,
        "loan_amount": float(dpr.loan_amount) if dpr.loan_amount else None,
        "cluster_name": dpr.cluster_name,
        "number_of_units": dpr.number_of_units,
        "swot_analysis": dpr.swot_analysis,
        "hard_interventions": dpr.hard_interventions,
        "soft_interventions": dpr.soft_interventions,
        "kpis": dpr.kpis,
        "government_grant": float(dpr.government_grant) if dpr.government_grant else None,
        "beneficiary_contribution": float(dpr.beneficiary_contribution) if dpr.beneficiary_contribution else None
    }
    
    output_path = f"storage/generated_dprs/{dpr_id}_dpr.pdf"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Generate PDF
    try:
        await generate_dpr_pdf(pdf_data, output_path)
        
        # Update DPR record
        await prisma.dpr.update(
            where={"id": dpr_id},
            data={"pdf_path": output_path, "status": "GENERATED"}
        )
        
        return {
            "message": "PDF generated successfully",
            "pdf_path": output_path,
            "dpr_id": dpr_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/{dpr_id}/download")
async def download_dpr(dpr_id: int, token: str = Depends(oauth2_scheme)):
    """Download DPR PDF"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    dpr = await prisma.dpr.find_unique(where={"id": dpr_id})
    if not dpr or not dpr.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if dpr.user_id != payload.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not Path(dpr.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found on server")
    
    return FileResponse(
        dpr.pdf_path,
        media_type='application/pdf',
        filename=f'{dpr.project_name}_DPR.pdf'
    )


@router.delete("/{dpr_id}")
async def delete_dpr(dpr_id: int, token: str = Depends(oauth2_scheme)):
    """Delete a DPR"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    dpr = await prisma.dpr.find_unique(where={"id": dpr_id})
    if not dpr:
        raise HTTPException(status_code=404, detail="DPR not found")
    
    if dpr.user_id != payload.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await prisma.dpr.delete(where={"id": dpr_id})
    
    return {"message": "DPR deleted successfully", "dpr_id": dpr_id}
