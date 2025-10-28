from playwright.async_api import async_playwright
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


async def generate_dpr_pdf(dpr_data: Dict[str, Any], output_path: str):
    """
    Generate a government-format DPR PDF using Playwright and Jinja2
    
    Args:
        dpr_data: Dictionary containing all DPR fields
        output_path: Path where PDF should be saved
    """
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Setup Jinja2 environment
    template_dir = Path("templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("dpr_template.html")
    
    # Prepare template context
    context = prepare_template_context(dpr_data)
    
    # Render HTML
    html_content = template.render(**context)
    
    # Generate PDF using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content(html_content)
        
        # Generate PDF with government-standard formatting
        await page.pdf(
            path=output_path,
            format='A4',
            margin={
                'top': '1in',
                'right': '0.75in',
                'bottom': '1in',
                'left': '0.75in'
            },
            print_background=True,
            display_header_footer=True,
            header_template='<div style="font-size:10px; text-align:center; width:100%;"></div>',
            footer_template='''
                <div style="font-size:10px; text-align:center; width:100%;">
                    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
                </div>
            '''
        )
        
        await browser.close()


def prepare_template_context(dpr_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare context data for template rendering"""
    
    # Extract financial projections
    financials = dpr_data.get("financial_projections", {})
    projections = financials.get("projections", [])
    
    # Prepare 5-year projection table
    projection_years = []
    for i, proj in enumerate(projections[:5], 1):
        projection_years.append({
            "year": i,
            "revenue": proj.get("revenue", 0),
            "expenses": proj.get("expenses", 0),
            "profit": proj.get("profit", 0)
        })
    
    # Extract market analysis
    market = dpr_data.get("market_analysis", {})
    
    # Extract SWOT
    swot = dpr_data.get("swot_analysis", {})
    
    # Calculate intervention costs
    hard_interventions = dpr_data.get("hard_interventions", [])
    soft_interventions = dpr_data.get("soft_interventions", [])
    
    total_hard_cost = sum(float(item.get("estimated_cost", 0)) for item in hard_interventions)
    total_soft_cost = sum(float(item.get("estimated_cost", 0)) for item in soft_interventions)
    
    # Prepare context
    context = {
        # Basic Information
        "project_name": dpr_data.get("project_name", "Untitled Project"),
        "sector": dpr_data.get("sector", ""),
        "location": dpr_data.get("location", ""),
        "cluster_name": dpr_data.get("cluster_name", ""),
        "spv_name": dpr_data.get("spv_name", ""),
        "number_of_units": dpr_data.get("number_of_units", 0),
        "number_of_workers": dpr_data.get("number_of_workers", 0),
        "diagnostic_agency": dpr_data.get("diagnostic_agency", ""),
        
        # Project Description
        "project_description": dpr_data.get("project_description", ""),
        
        # Financial Summary
        "investment_amount": float(dpr_data.get("investment_amount", 0)),
        "government_grant": float(dpr_data.get("government_grant", 0)),
        "beneficiary_contribution": float(dpr_data.get("beneficiary_contribution", 0)),
        "grant_percentage": float(dpr_data.get("grant_percentage", 70)),
        "loan_amount": float(dpr_data.get("loan_amount", 0)) if dpr_data.get("loan_amount") else 0,
        "employment": dpr_data.get("employment", 0),
        
        # Financial Metrics
        "npv": financials.get("npv", 0),
        "irr": financials.get("irr", "0%"),
        "break_even": financials.get("break_even_period", "N/A"),
        
        # Projections
        "projection_years": projection_years,
        
        # Market Analysis
        "market_size": market.get("market_size", "N/A"),
        "target_customers": market.get("target_customers", []),
        "competition": market.get("competition", ""),
        "market_opportunities": market.get("opportunities", []),
        "market_challenges": market.get("challenges", []),
        "market_trends": market.get("trends", []),
        
        # SWOT Analysis
        "strengths": swot.get("strengths", []),
        "weaknesses": swot.get("weaknesses", []),
        "opportunities": swot.get("opportunities", []),
        "threats": swot.get("threats", []),
        
        # Interventions
        "hard_interventions": hard_interventions,
        "soft_interventions": soft_interventions,
        "total_hard_cost": total_hard_cost,
        "total_soft_cost": total_soft_cost,
        "total_intervention_cost": total_hard_cost + total_soft_cost,
        
        # KPIs
        "kpis": dpr_data.get("kpis", []),
        
        # Implementation Timeline
        "implementation_timeline": dpr_data.get("implementation_timeline", []),
        "project_duration_months": dpr_data.get("project_duration_months", 36),
        
        # Sustainability Plan
        "sustainability_plan": dpr_data.get("sustainability_plan", {}),
        
        # Metadata
        "generated_date": datetime.now().strftime("%d %B %Y"),
        "generated_time": datetime.now().strftime("%I:%M %p"),
    }
    
    return context


def format_currency(amount: float) -> str:
    """Format currency in Indian Rupees format"""
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.2f}%"
