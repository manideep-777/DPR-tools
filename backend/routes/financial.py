"""
Financial Projections API Endpoints
Handles calculation and retrieval of financial projections and summaries
"""
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from decimal import Decimal
from datetime import datetime, timezone
from middleware.auth import get_current_user, CurrentUser
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Prisma client
prisma = Prisma()

router = APIRouter(prefix="/financial", tags=["Financial Projections"])


# ============================================================
# Pydantic Models
# ============================================================

class FinancialProjectionMonth(BaseModel):
    month_number: int
    revenue: float
    fixed_costs: float
    variable_costs: float
    profit_loss: float
    cumulative_profit_loss: float


class FinancialSummaryResponse(BaseModel):
    form_id: int
    business_name: str
    breakeven_months: int
    roi_percentage: float
    payback_period_months: int
    npv: float
    profit_margin_percentage: float
    calculated_at: str


class FinancialCalculationResponse(BaseModel):
    success: bool
    message: str
    form_id: int
    projections_count: int
    summary: Optional[dict] = None


class FinancialProjectionsResponse(BaseModel):
    form_id: int
    business_name: str
    total_months: int
    projections: List[FinancialProjectionMonth]
    summary: Optional[FinancialSummaryResponse] = None


# ============================================================
# Helper Functions
# ============================================================

async def get_form_data(form_id: int, user_id: int):
    """
    Retrieve complete form data with all required details for calculations
    """
    # Connect to database if not connected
    if not prisma.is_connected():
        await prisma.connect()
    
    form = await prisma.dprform.find_unique(
        where={"id": form_id},
        include={
            "financialDetails": True,
            "revenueAssumptions": True,
            "costDetails": True,
            "businessDetails": True
        }
    )
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form with ID {form_id} not found"
        )
    
    if form.userId != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this form"
        )
    
    # Validate required data
    if not form.financialDetails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial details are required for calculations"
        )
    
    if not form.revenueAssumptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Revenue assumptions are required for calculations"
        )
    
    if not form.costDetails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cost details are required for calculations"
        )
    
    return form


def calculate_monthly_projections(form) -> List[dict]:
    """
    Calculate 36-month financial projections
    
    Formula breakdown:
    - Revenue = Product Price × Monthly Sales Quantity
    - Fixed Costs = Sum of all fixed monthly costs
    - Variable Costs = Raw materials (varies with production)
    - Profit/Loss = Revenue - Fixed Costs - Variable Costs
    - Cumulative Profit/Loss = Running total of profit/loss
    """
    financial = form.financialDetails
    revenue_assumptions = form.revenueAssumptions
    cost_details = form.costDetails
    
    # Get baseline values
    product_price = float(revenue_assumptions.productPrice)
    growth_rate = float(revenue_assumptions.growthRatePercentage) / 100
    
    # Sales quantities by year
    sales_year_1 = revenue_assumptions.monthlySalesQuantityYear1
    sales_year_2 = revenue_assumptions.monthlySalesQuantityYear2
    sales_year_3 = revenue_assumptions.monthlySalesQuantityYear3
    
    # Monthly costs
    fixed_monthly = (
        float(cost_details.laborCostMonthly) +
        float(cost_details.utilitiesCostMonthly) +
        float(cost_details.rentMonthly) +
        float(cost_details.marketingCostMonthly) +
        float(cost_details.otherFixedCostsMonthly)
    )
    
    variable_monthly_base = float(cost_details.rawMaterialCostMonthly)
    
    projections = []
    cumulative_profit_loss = 0.0
    
    for month in range(1, 37):  # 36 months
        # Determine sales quantity based on year
        if month <= 12:
            sales_quantity = sales_year_1
        elif month <= 24:
            sales_quantity = sales_year_2
        else:
            sales_quantity = sales_year_3
        
        # Calculate revenue
        revenue = product_price * sales_quantity
        
        # Variable costs scale with production
        variable_costs = variable_monthly_base
        
        # Calculate profit/loss
        profit_loss = revenue - fixed_monthly - variable_costs
        
        # Update cumulative
        cumulative_profit_loss += profit_loss
        
        projections.append({
            "month_number": month,
            "revenue": revenue,
            "fixed_costs": fixed_monthly,
            "variable_costs": variable_costs,
            "profit_loss": profit_loss,
            "cumulative_profit_loss": cumulative_profit_loss
        })
    
    return projections


def calculate_summary_metrics(projections: List[dict], total_investment: float) -> dict:
    """
    Calculate financial summary metrics
    
    Metrics:
    - Break-even month: First month where cumulative profit > 0
    - ROI: (Total profit after 36 months / Total investment) × 100
    - Payback period: Months until cumulative profit = investment
    - NPV: Simplified (using 10% discount rate)
    - Profit margin: Average monthly profit margin
    """
    # Break-even month
    breakeven_months = 0
    for proj in projections:
        if proj["cumulative_profit_loss"] > 0:
            breakeven_months = proj["month_number"]
            break
    
    if breakeven_months == 0:
        breakeven_months = 36  # Didn't break even in 36 months
    
    # ROI calculation
    final_cumulative_profit = projections[-1]["cumulative_profit_loss"]
    roi_percentage = (final_cumulative_profit / total_investment) * 100 if total_investment > 0 else 0
    
    # Payback period
    payback_period_months = 0
    for proj in projections:
        if proj["cumulative_profit_loss"] >= total_investment:
            payback_period_months = proj["month_number"]
            break
    
    if payback_period_months == 0:
        payback_period_months = 36  # Didn't pay back in 36 months
    
    # NPV calculation (simplified with 10% annual discount rate = 0.83% monthly)
    discount_rate_monthly = 0.0083
    npv = 0.0
    for proj in projections:
        discounted_cash_flow = proj["profit_loss"] / ((1 + discount_rate_monthly) ** proj["month_number"])
        npv += discounted_cash_flow
    
    npv -= total_investment  # Subtract initial investment
    
    # Average profit margin
    total_revenue = sum(p["revenue"] for p in projections if p["revenue"] > 0)
    total_profit = sum(p["profit_loss"] for p in projections)
    profit_margin_percentage = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "breakeven_months": breakeven_months,
        "roi_percentage": round(roi_percentage, 2),
        "payback_period_months": payback_period_months,
        "npv": round(npv, 2),
        "profit_margin_percentage": round(profit_margin_percentage, 2)
    }


# ============================================================
# API Endpoints
# ============================================================

@router.post("/{form_id}/calculate",
             response_model=FinancialCalculationResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Calculate financial projections",
             description="Calculate 36-month financial projections and summary metrics for a DPR form")
async def calculate_financial_projections(
    form_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate comprehensive financial projections
    
    This endpoint:
    1. Retrieves form data (financial, revenue, costs)
    2. Calculates month-by-month projections (36 months)
    3. Computes summary metrics (ROI, break-even, NPV, etc.)
    4. Stores results in database
    
    Returns:
    - Success message with projection count and summary metrics
    """
    try:
        # Get form data and validate
        form = await get_form_data(form_id, current_user.id)
        
        logger.info(f"Calculating financial projections for form {form_id}")
        
        # Calculate monthly projections
        projections = calculate_monthly_projections(form)
        
        # Calculate summary metrics
        total_investment = float(form.financialDetails.totalInvestmentAmount)
        summary_metrics = calculate_summary_metrics(projections, total_investment)
        
        # Ensure database connection
        if not prisma.is_connected():
            await prisma.connect()
        
        # Delete existing projections for this form
        await prisma.financialprojection.delete_many(
            where={"formId": form_id}
        )
        
        # Store projections in database
        for proj in projections:
            await prisma.financialprojection.create(
                data={
                    "formId": form_id,
                    "monthNumber": proj["month_number"],
                    "revenue": Decimal(str(proj["revenue"])),
                    "fixedCosts": Decimal(str(proj["fixed_costs"])),
                    "variableCosts": Decimal(str(proj["variable_costs"])),
                    "profitLoss": Decimal(str(proj["profit_loss"])),
                    "cumulativeProfitLoss": Decimal(str(proj["cumulative_profit_loss"]))
                }
            )
        
        # Delete existing summary
        await prisma.financialsummary.delete_many(
            where={"formId": form_id}
        )
        
        # Store summary
        await prisma.financialsummary.create(
            data={
                "formId": form_id,
                "breakevenMonths": summary_metrics["breakeven_months"],
                "roiPercentage": Decimal(str(summary_metrics["roi_percentage"])),
                "paybackPeriodMonths": summary_metrics["payback_period_months"],
                "npv": Decimal(str(summary_metrics["npv"])),
                "profitMarginPercentage": Decimal(str(summary_metrics["profit_margin_percentage"])),
                "calculatedAt": datetime.now(timezone.utc)
            }
        )
        
        logger.info(f"✅ Successfully calculated projections for form {form_id}")
        logger.info(f"   Break-even: {summary_metrics['breakeven_months']} months")
        logger.info(f"   ROI: {summary_metrics['roi_percentage']}%")
        logger.info(f"   Payback: {summary_metrics['payback_period_months']} months")
        
        return FinancialCalculationResponse(
            success=True,
            message="Financial projections calculated successfully",
            form_id=form_id,
            projections_count=len(projections),
            summary=summary_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating financial projections for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate financial projections: {str(e)}"
        )


@router.get("/{form_id}/projections",
            response_model=FinancialProjectionsResponse,
            summary="Get financial projections",
            description="Retrieve calculated financial projections for a form")
async def get_financial_projections(
    form_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all financial projections for a form
    
    Returns:
    - 36-month projections with revenue, costs, profit/loss
    - Summary metrics (ROI, break-even, etc.)
    """
    try:
        # Ensure database connection
        if not prisma.is_connected():
            await prisma.connect()
        
        # Verify form ownership
        form = await prisma.dprform.find_unique(
            where={"id": form_id},
            include={"businessDetails": True}
        )
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with ID {form_id} not found"
            )
        
        if form.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this form"
            )
        
        # Get projections
        projections = await prisma.financialprojection.find_many(
            where={"formId": form_id},
            order={"monthNumber": "asc"}
        )
        
        if not projections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No financial projections found. Please calculate projections first."
            )
        
        # Get summary
        summary = await prisma.financialsummary.find_unique(
            where={"formId": form_id}
        )
        
        # Format response
        projection_list = [
            FinancialProjectionMonth(
                month_number=p.monthNumber,
                revenue=float(p.revenue),
                fixed_costs=float(p.fixedCosts),
                variable_costs=float(p.variableCosts),
                profit_loss=float(p.profitLoss),
                cumulative_profit_loss=float(p.cumulativeProfitLoss)
            )
            for p in projections
        ]
        
        summary_response = None
        if summary:
            summary_response = FinancialSummaryResponse(
                form_id=form_id,
                business_name=form.businessName,
                breakeven_months=summary.breakevenMonths,
                roi_percentage=float(summary.roiPercentage),
                payback_period_months=summary.paybackPeriodMonths,
                npv=float(summary.npv),
                profit_margin_percentage=float(summary.profitMarginPercentage),
                calculated_at=summary.calculatedAt.isoformat()
            )
        
        return FinancialProjectionsResponse(
            form_id=form_id,
            business_name=form.businessName,
            total_months=len(projection_list),
            projections=projection_list,
            summary=summary_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving financial projections for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve financial projections: {str(e)}"
        )


@router.get("/{form_id}/summary",
            response_model=FinancialSummaryResponse,
            summary="Get financial summary",
            description="Retrieve financial summary metrics (ROI, NPV, break-even, etc.)")
async def get_financial_summary(
    form_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get financial summary for a form
    
    Returns:
    - Break-even month
    - ROI percentage
    - Payback period
    - NPV
    - Profit margin percentage
    """
    try:
        # Ensure database connection
        if not prisma.is_connected():
            await prisma.connect()
        
        # Verify form ownership
        form = await prisma.dprform.find_unique(
            where={"id": form_id}
        )
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with ID {form_id} not found"
            )
        
        if form.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this form"
            )
        
        # Get summary
        summary = await prisma.financialsummary.find_unique(
            where={"formId": form_id}
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No financial summary found. Please calculate projections first."
            )
        
        return FinancialSummaryResponse(
            form_id=form_id,
            business_name=form.businessName,
            breakeven_months=summary.breakevenMonths,
            roi_percentage=float(summary.roiPercentage),
            payback_period_months=summary.paybackPeriodMonths,
            npv=float(summary.npv),
            profit_margin_percentage=float(summary.profitMarginPercentage),
            calculated_at=summary.calculatedAt.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving financial summary for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve financial summary: {str(e)}"
        )
