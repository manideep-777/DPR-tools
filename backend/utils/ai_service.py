"""
AI Service for generating DPR content using Google Gemini API
"""
import os
import google.generativeai as genai
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# Available sections for AI generation
AVAILABLE_SECTIONS = [
    "executive_summary",
    "market_analysis",
    "competitive_analysis",
    "marketing_strategy",
    "operational_plan",
    "risk_analysis",
    "swot_analysis",
    "implementation_roadmap"
]


class AIService:
    """Service class for AI content generation using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini API with API key from environment"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-2.5-flash"  # Store model name
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. AI generation will fail.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use gemini-2.5-flash - stable, fast, and cost-effective
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"✅ Gemini API initialized successfully with {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {str(e)}")
                self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None
    
    def get_model_name(self) -> str:
        """Get the name of the AI model being used"""
        return self.model_name if self.model is not None else "unknown"
    
    def generate_section(self, section_name: str, form_data: Dict) -> Optional[str]:
        """
        Generate content for a specific section using form data
        
        Args:
            section_name: Name of the section to generate
            form_data: Dictionary containing all form data for context
        
        Returns:
            Generated text content or None if generation fails
        """
        if not self.is_available():
            logger.error("AI service not available - check GOOGLE_API_KEY")
            return None
        
        if section_name not in AVAILABLE_SECTIONS:
            logger.error(f"Invalid section name: {section_name}")
            return None
        
        try:
            # Build prompt based on section and form data
            prompt = self._build_prompt(section_name, form_data)
            
            # Generate content using Gemini
            logger.info(f"Generating {section_name} for form {form_data.get('business_name', 'Unknown')}")
            response = self.model.generate_content(prompt)
            
            # Extract and return text
            generated_text = response.text
            logger.info(f"✅ Successfully generated {len(generated_text)} characters for {section_name}")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating {section_name}: {str(e)}")
            return None
    
    def _build_prompt(self, section_name: str, form_data: Dict) -> str:
        """
        Build a detailed prompt for content generation
        
        Args:
            section_name: Section to generate
            form_data: Complete form data
        
        Returns:
            Formatted prompt string
        """
        business_name = form_data.get("business_name", "the business")
        
        # Extract relevant data
        entrepreneur = form_data.get("entrepreneur_details", {})
        business = form_data.get("business_details", {})
        product = form_data.get("product_details", {})
        financial = form_data.get("financial_details", {})
        revenue = form_data.get("revenue_assumptions", {})
        cost = form_data.get("cost_details", {})
        staffing = form_data.get("staffing_details", {})
        timeline = form_data.get("timeline_details", {})
        
        # Base context that all sections will use
        base_context = f"""
You are an expert business consultant writing a Detailed Project Report (DPR) for an MSME (Micro, Small, and Medium Enterprise) in India.

Business Name: {business_name}
Sector: {business.get('sector', 'Not specified')}
Legal Structure: {business.get('legal_structure', 'Not specified')}
Location: {business.get('location', 'Not specified')}
Total Investment: ₹{financial.get('total_investment_amount', 'Not specified')}
Product/Service: {product.get('product_name', 'Not specified')}

Entrepreneur Background:
- Name: {entrepreneur.get('full_name', 'Not specified')}
- Education: {entrepreneur.get('education', 'Not specified')}
- Experience: {entrepreneur.get('years_of_experience', 'Not specified')} years

"""
        
        # Section-specific prompts
        prompts = {
            "executive_summary": f"""
{base_context}

Write a comprehensive Executive Summary (400-500 words) for this DPR that includes:
1. Brief introduction to the business and entrepreneur
2. Project overview and objectives
3. Key highlights of the business opportunity
4. Investment requirements and funding structure
5. Expected returns and viability
6. Unique value proposition

Make it compelling and professional, suitable for bank loan applications and government schemes.
""",
            
            "market_analysis": f"""
{base_context}

Write a detailed Market Analysis (500-600 words) that covers:
1. Industry overview for {business.get('sector', 'the sector')} in India
2. Market size and growth trends
3. Target customer segments: {product.get('target_customers', 'Various segments')}
4. Demand analysis and market potential
5. Key market drivers and opportunities
6. Barriers to entry and challenges

Use realistic Indian market data and trends. Be specific to {business.get('location', 'the region')}.
""",
            
            "competitive_analysis": f"""
{base_context}

Product/Service: {product.get('description', 'Not provided')}
Key Features: {product.get('key_features', [])}
Unique Selling Points: {product.get('unique_selling_points', 'Not specified')}

Write a Competitive Analysis (400-500 words) covering:
1. Overview of existing competitors in {business.get('sector', 'the sector')}
2. Competitive landscape and market positioning
3. Comparative advantages of this business
4. Points of differentiation and unique value
5. Competitive strategy and positioning

Be realistic about competition while highlighting the business's strengths.
""",
            
            "marketing_strategy": f"""
{base_context}

Monthly Marketing Budget: ₹{cost.get('marketing_cost_monthly', 'Not specified')}
Target Customers: {product.get('target_customers', 'Not specified')}

Write a Marketing Strategy (400-500 words) that includes:
1. Marketing objectives and goals
2. Target market segmentation and positioning
3. Marketing channels and tactics (digital, traditional)
4. Pricing strategy: Product price ₹{revenue.get('product_price', 'TBD')}
5. Promotional activities and campaigns
6. Customer acquisition and retention strategy
7. Budget allocation and timeline

Focus on cost-effective strategies suitable for MSMEs.
""",
            
            "operational_plan": f"""
{base_context}

Production Details:
- Planned Capacity: {product.get('planned_capacity', 'Not specified')} units
- Total Employees: {staffing.get('total_employees', 'Not specified')}
- Location: {business.get('address', 'Not specified')}

Timeline:
- Land/Setup: {timeline.get('land_acquisition_months', 0)} months
- Construction: {timeline.get('construction_months', 0)} months
- Machinery Installation: {timeline.get('machinery_installation_months', 0)} months
- Commercial Production Start: Month {timeline.get('commercial_production_start_month', 'TBD')}

Write an Operational Plan (500-600 words) covering:
1. Production process and workflow
2. Facility requirements and layout
3. Machinery and equipment needs
4. Quality control measures: {product.get('quality_certifications', 'Standard quality practices')}
5. Supply chain management
6. Staffing plan and organizational structure
7. Day-to-day operations management

Be specific and practical for an MSME setting.
""",
            
            "risk_analysis": f"""
{base_context}

Investment Amount: ₹{financial.get('total_investment_amount', 'Not specified')}
Loan Required: ₹{financial.get('loan_required', 'Not specified')}
Working Capital: ₹{financial.get('working_capital', 'Not specified')}

Write a Risk Analysis (400-500 words) that identifies:
1. Market risks (demand fluctuation, competition)
2. Financial risks (funding, cash flow)
3. Operational risks (supply chain, production)
4. Regulatory and compliance risks
5. Technology and obsolescence risks
6. Mitigation strategies for each major risk
7. Contingency planning

Be realistic but balanced - acknowledge risks while showing preparedness.
""",
            
            "swot_analysis": f"""
{base_context}

Entrepreneur Experience: {entrepreneur.get('years_of_experience', 0)} years
Previous Business: {entrepreneur.get('previous_business_experience', 'None specified')}
Technical Skills: {entrepreneur.get('technical_skills', 'Not specified')}
USPs: {product.get('unique_selling_points', 'Not specified')}

Write a SWOT Analysis (400-500 words) covering:

Strengths:
- Entrepreneur's experience and skills
- Product/service unique features
- Location advantages
- Financial readiness

Weaknesses:
- Resource constraints
- Market presence
- Experience gaps
- Scalability challenges

Opportunities:
- Market growth potential
- Government schemes and support
- Technology adoption
- Expansion possibilities

Threats:
- Competition
- Market changes
- Economic factors
- Regulatory changes

Be honest and comprehensive. Each quadrant should have 4-5 specific points.
""",
            
            "implementation_roadmap": f"""
{base_context}

Timeline Details:
- Land Acquisition: {timeline.get('land_acquisition_months', 0)} months
- Construction: {timeline.get('construction_months', 0)} months
- Machinery Installation: {timeline.get('machinery_installation_months', 0)} months
- Trial Production: {timeline.get('trial_production_months', 0)} months
- Commercial Production: Month {timeline.get('commercial_production_start_month', 'TBD')}

Sales Growth:
- Year 1: {revenue.get('monthly_sales_quantity_year1', 'TBD')} units/month
- Year 2: {revenue.get('monthly_sales_quantity_year2', 'TBD')} units/month
- Year 3: {revenue.get('monthly_sales_quantity_year3', 'TBD')} units/month

Write an Implementation Roadmap (500-600 words) with:
1. Phase-wise implementation plan
2. Key milestones and deliverables
3. Resource allocation timeline
4. Funding and cash flow management
5. Scaling strategy over 3 years
6. Success metrics and KPIs
7. Review and adjustment mechanisms

Create a realistic, achievable roadmap with clear quarterly milestones.
"""
        }
        
        return prompts.get(section_name, f"Generate content for {section_name} section of a DPR for {business_name}.")


# Singleton instance
ai_service = AIService()
