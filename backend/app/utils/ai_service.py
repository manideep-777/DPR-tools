import google.generativeai as genai
from app.config import settings
from typing import Dict, Any, List
import json

# Configure Gemini only if API key is provided and valid
try:
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        USE_AI = True
    else:
        model = None
        USE_AI = False
except Exception as e:
    print(f"Gemini AI setup error: {e}")
    model = None
    USE_AI = False


async def generate_swot_analysis(
    sector: str,
    location: str,
    project_name: str,
    cluster_info: Dict[str, Any] = None
) -> Dict[str, List[str]]:
    """Generate SWOT analysis for the cluster/project"""
    
    fallback_swot = {
        "strengths": [
            f"Established presence in {sector} sector",
            f"Skilled workforce availability in {location}",
            "Existing market knowledge and customer base",
            "Local raw material availability"
        ],
        "weaknesses": [
            "Limited access to modern technology",
            "Lack of adequate infrastructure",
            "Insufficient working capital",
            "Low bargaining power with suppliers"
        ],
        "opportunities": [
            "Growing demand for quality products",
            "Government support schemes for MSMEs",
            "Export market potential",
            "Technology upgradation possibilities"
        ],
        "threats": [
            "Competition from organized sector",
            "Fluctuating raw material costs",
            "Changing market preferences",
            "Environmental compliance requirements"
        ]
    }
    
    if not USE_AI:
        return fallback_swot
    
    cluster_context = ""
    if cluster_info:
        cluster_context = f"""
        Cluster Details:
        - Number of Units: {cluster_info.get('number_of_units', 'Not specified')}
        - Workers: {cluster_info.get('number_of_workers', 'Not specified')}
        - SPV: {cluster_info.get('spv_name', 'Not specified')}
        """
    
    prompt = f"""
    Conduct a comprehensive SWOT analysis for an MSME cluster/project:
    
    Project: {project_name}
    Sector: {sector}
    Location: {location}
    {cluster_context}
    
    Provide a detailed SWOT analysis in JSON format:
    {{
        "strengths": [4-5 specific strengths],
        "weaknesses": [4-5 specific weaknesses],
        "opportunities": [4-5 specific opportunities],
        "threats": [4-5 specific threats]
    }}
    
    Make it specific to the {sector} sector in {location}.
    Return ONLY valid JSON without code blocks or markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating SWOT analysis: {e}")
        return fallback_swot


async def generate_interventions(
    sector: str,
    swot_analysis: Dict[str, List[str]],
    investment_amount: float
) -> Dict[str, List[Dict[str, Any]]]:
    """Generate Hard and Soft interventions based on SWOT"""
    
    fallback_interventions = {
        "hard": [
            {
                "name": "Common Facility Center",
                "description": "Establishment of shared workspace and equipment facility",
                "estimated_cost": investment_amount * 0.4,
                "timeline_months": 12
            },
            {
                "name": "Machinery & Equipment",
                "description": "Modern machinery for production efficiency",
                "estimated_cost": investment_amount * 0.3,
                "timeline_months": 6
            },
            {
                "name": "Testing & Quality Lab",
                "description": "Quality control and testing facility",
                "estimated_cost": investment_amount * 0.1,
                "timeline_months": 8
            }
        ],
        "soft": [
            {
                "name": "Skill Development Training",
                "description": "Technical and managerial training programs",
                "estimated_cost": investment_amount * 0.05,
                "timeline_months": 24
            },
            {
                "name": "Marketing & Branding",
                "description": "Brand development and market linkage programs",
                "estimated_cost": investment_amount * 0.08,
                "timeline_months": 18
            },
            {
                "name": "Technology Transfer",
                "description": "Adoption of new technologies and best practices",
                "estimated_cost": investment_amount * 0.07,
                "timeline_months": 12
            }
        ]
    }
    
    if not USE_AI:
        return fallback_interventions
    
    weaknesses_str = ", ".join(swot_analysis.get("weaknesses", []))
    opportunities_str = ", ".join(swot_analysis.get("opportunities", []))
    
    prompt = f"""
    Based on this SWOT analysis for a {sector} MSME cluster, suggest interventions:
    
    Key Weaknesses to Address: {weaknesses_str}
    Opportunities to Leverage: {opportunities_str}
    Total Investment: ₹{investment_amount}
    
    Provide interventions in TWO categories:
    
    HARD INTERVENTIONS (Infrastructure/Equipment - 70-80% of budget):
    - Common Facility Center
    - Machinery & Equipment
    - Testing Labs
    - Raw Material Bank
    - Infrastructure
    
    SOFT INTERVENTIONS (Capacity Building - 20-30% of budget):
    - Training Programs
    - Marketing Support
    - Technology Transfer
    - Quality Certification
    - Market Linkages
    
    Return JSON format:
    {{
        "hard": [
            {{"name": "", "description": "", "estimated_cost": 0, "timeline_months": 0}}
        ],
        "soft": [
            {{"name": "", "description": "", "estimated_cost": 0, "timeline_months": 0}}
        ]
    }}
    
    Ensure costs add up to approximately ₹{investment_amount}.
    Return ONLY valid JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating interventions: {e}")
        return fallback_interventions


async def generate_kpis(
    sector: str,
    project_name: str,
    interventions: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """Generate Key Performance Indicators"""
    
    fallback_kpis = [
        {
            "indicator": "Number of Units Benefited",
            "baseline": 0,
            "year1_target": 20,
            "year2_target": 50,
            "year3_target": 75,
            "unit": "numbers"
        },
        {
            "indicator": "Employment Generated",
            "baseline": 0,
            "year1_target": 50,
            "year2_target": 150,
            "year3_target": 250,
            "unit": "persons"
        },
        {
            "indicator": "Production Capacity Increase",
            "baseline": 100,
            "year1_target": 120,
            "year2_target": 150,
            "year3_target": 200,
            "unit": "percentage"
        },
        {
            "indicator": "Revenue Growth",
            "baseline": 100,
            "year1_target": 115,
            "year2_target": 135,
            "year3_target": 160,
            "unit": "percentage"
        },
        {
            "indicator": "Quality Certifications Obtained",
            "baseline": 0,
            "year1_target": 5,
            "year2_target": 15,
            "year3_target": 25,
            "unit": "numbers"
        }
    ]
    
    if not USE_AI:
        return fallback_kpis
    
    hard_interventions = [item["name"] for item in interventions.get("hard", [])]
    soft_interventions = [item["name"] for item in interventions.get("soft", [])]
    
    prompt = f"""
    Define measurable KPIs for this {sector} MSME cluster project:
    
    Project: {project_name}
    Hard Interventions: {", ".join(hard_interventions)}
    Soft Interventions: {", ".join(soft_interventions)}
    
    Provide 5-7 SMART KPIs with baseline and 3-year targets:
    
    Return JSON format:
    [
        {{
            "indicator": "KPI name",
            "baseline": 0,
            "year1_target": 0,
            "year2_target": 0,
            "year3_target": 0,
            "unit": "numbers/percentage/amount"
        }}
    ]
    
    Focus on: units benefited, employment, production, revenue, quality, market access.
    Return ONLY valid JSON array.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating KPIs: {e}")
        return fallback_kpis


async def generate_market_analysis(sector: str, location: str, project_name: str) -> Dict[str, Any]:
    """Generate market analysis using Gemini AI"""
    
    # Return fallback data if AI is not configured
    if not USE_AI:
        return {
            "market_size": f"The {sector} market in {location} shows steady growth potential with increasing demand.",
            "target_customers": ["Local businesses", "Individual consumers", "Institutional buyers"],
            "competition": f"Moderate competition exists in the {sector} sector with opportunities for differentiation.",
            "opportunities": ["Growing market demand", "Technology adoption", "Export potential"],
            "challenges": ["Raw material sourcing", "Skilled workforce availability", "Market competition"],
            "trends": ["Digital transformation", "Sustainability focus", "Quality consciousness"]
        }
    
    prompt = f"""
    Generate a comprehensive market analysis for an MSME project with the following details:
    - Sector: {sector}
    - Location: {location}
    - Project Name: {project_name}
    
    Provide the analysis in JSON format with these sections:
    1. market_size: Current market size and growth potential (2-3 sentences)
    2. target_customers: Target customer segments (2-3 bullet points)
    3. competition: Competitive landscape analysis (2-3 sentences)
    4. opportunities: Market opportunities (2-3 bullet points)
    5. challenges: Potential challenges (2-3 bullet points)
    6. trends: Current market trends (2-3 bullet points)
    
    Return ONLY valid JSON without code blocks or markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response text
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating market analysis: {e}")
        return {
            "market_size": f"The {sector} market in {location} shows steady growth potential.",
            "target_customers": ["Local businesses", "Individual consumers", "Institutional buyers"],
            "competition": f"Moderate competition exists in the {sector} sector with opportunities for differentiation.",
            "opportunities": ["Growing market demand", "Technology adoption", "Export potential"],
            "challenges": ["Raw material sourcing", "Skilled workforce availability", "Market competition"],
            "trends": ["Digital transformation", "Sustainability focus", "Quality consciousness"]
        }


async def generate_financial_projections(
    investment: float,
    sector: str,
    employment: int,
    project_duration_months: int = 36
) -> Dict[str, Any]:
    """Generate financial projections using AI"""
    
    years = min(5, (project_duration_months + 11) // 12)  # Convert months to years, max 5
    
    # Calculate fallback projections
    base_revenue = investment * 0.8
    fallback_data = {
        "revenue_projections": [base_revenue * (1 + 0.15 * i) for i in range(years)],
        "operating_expenses": [base_revenue * 0.75 * (1 + 0.13 * i) for i in range(years)],
        "profit_projections": [base_revenue * 0.25 * (1 + 0.17 * i) for i in range(years)],
        "break_even_period": "18 months",
        "roi_percentage": "45%",
        "npv": investment * 0.35,
        "irr": "22%"
    }
    
    # Return fallback if AI not configured
    if not USE_AI:
        return fallback_data
    
    prompt = f"""
    Generate realistic {years}-year financial projections for an MSME with:
    - Total Investment: ₹{investment}
    - Sector: {sector}
    - Employment: {employment} persons
    - Project Duration: {project_duration_months} months
    
    Provide projections in JSON format:
    {{
        "revenue_projections": [year1, year2, year3, year4, year5],
        "operating_expenses": [year1, year2, year3, year4, year5],
        "profit_projections": [year1, year2, year3, year4, year5],
        "break_even_period": "X months",
        "roi_percentage": "X%",
        "npv": estimated NPV value,
        "irr": "X%"
    }}
    
    Use realistic growth rates (10-20% per year) and operating margins (15-25%) for {sector}.
    Return ONLY valid JSON without code blocks or markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating financial projections: {e}")
        return fallback_data


async def generate_executive_summary(dpr_data: Dict[str, Any]) -> str:
    """Generate executive summary for DPR"""
    
    fallback_summary = f"""
This Detailed Project Report presents {dpr_data.get('project_name')}, a {dpr_data.get('sector')} venture 
located in {dpr_data.get('location')}. The project aims to {dpr_data.get('project_description')}

With a total investment of ₹{dpr_data.get('investment_amount')}, this project addresses the growing 
market demand in the {dpr_data.get('sector')} sector. The business model leverages modern practices 
and technology to deliver high-quality products/services to the target market.

The project is expected to generate steady revenue growth, create employment opportunities, and contribute 
to the local economy. Financial projections indicate a healthy return on investment with manageable risks.
"""
    
    # Return fallback if AI not configured
    if not USE_AI:
        return fallback_summary
    
    prompt = f"""
    Write a professional executive summary for a Detailed Project Report with these details:
    
    Project Name: {dpr_data.get('project_name')}
    Sector: {dpr_data.get('sector')}
    Location: {dpr_data.get('location')}
    Investment: ₹{dpr_data.get('investment_amount')}
    Description: {dpr_data.get('project_description')}
    
    Write 200-250 words covering:
    1. Project overview
    2. Business opportunity
    3. Investment highlights
    4. Expected outcomes
    
    Keep it professional and bank-ready. Return only the summary text.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating executive summary: {e}")
        return fallback_summary
