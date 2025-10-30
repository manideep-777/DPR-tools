"""
Government Schemes Matching API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma
from middleware.auth import get_current_user, CurrentUser
from models.scheme_models import SchemeMatchRequest, SchemeMatchResponse, SchemeResponse
from utils.ai_service import ai_service
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])

# Prisma client instance (shared, managed by main.py lifespan)
prisma = Prisma()


async def ai_match_schemes(form_data: dict, schemes: List[dict], max_results: int = 10) -> List[dict]:
    """
    Use AI to intelligently match and rank government schemes based on comprehensive business analysis
    
    Args:
        form_data: Complete business and financial details
        schemes: List of available government schemes
        max_results: Maximum number of schemes to return
        
    Returns:
        List of matched schemes with AI-generated scores and recommendations
    """
    try:
        # Prepare business context for AI
        business_context = f"""
Business Name: {form_data.get('business_name', 'N/A')}

BUSINESS DETAILS:
- Sector: {form_data.get('business_details', {}).get('sector', 'N/A')}
- Sub-sector: {form_data.get('business_details', {}).get('sub_sector', 'N/A')}
- Legal Structure: {form_data.get('business_details', {}).get('legal_structure', 'N/A')}
- Location: {form_data.get('business_details', {}).get('location', 'N/A')}
- Address: {form_data.get('business_details', {}).get('address', 'N/A')}

FINANCIAL DETAILS:
- Total Investment: ₹{form_data.get('financial_details', {}).get('total_investment_amount', 0):,.0f}
- Land Cost: ₹{form_data.get('financial_details', {}).get('land_cost', 0):,.0f}
- Building Cost: ₹{form_data.get('financial_details', {}).get('building_cost', 0):,.0f}
- Machinery Cost: ₹{form_data.get('financial_details', {}).get('machinery_cost', 0):,.0f}
- Working Capital: ₹{form_data.get('financial_details', {}).get('working_capital', 0):,.0f}
- Own Contribution: ₹{form_data.get('financial_details', {}).get('own_contribution', 0):,.0f}
- Loan Required: ₹{form_data.get('financial_details', {}).get('loan_required', 0):,.0f}
"""

        # Prepare schemes summary for AI
        schemes_summary = []
        for idx, scheme in enumerate(schemes, 1):
            scheme_info = f"""
{idx}. {scheme.get('schemeName')}
   - Type: {scheme.get('schemeType')}
   - Ministry: {scheme.get('ministry')}
   - Description: {scheme.get('description', '')[:200]}...
   - Eligible Sectors: {', '.join(scheme.get('eligibleSectors', []))}
   - Eligible States: {', '.join(scheme.get('eligibleStates', []))}
   - Investment Range: ₹{scheme.get('minInvestment', 0):,.0f} - ₹{scheme.get('maxInvestment', 0):,.0f}
   - Subsidy: {scheme.get('subsidyPercentage', 'N/A')}% (Max: ₹{scheme.get('maxSubsidyAmount', 0):,.0f})
   - Eligibility: {scheme.get('eligibilityCriteria', 'N/A')[:150]}...
"""
            schemes_summary.append(scheme_info)
        
        # AI Prompt for intelligent matching
        prompt = f"""You are an expert government scheme advisor for MSMEs in India. Analyze the following business details and match them with the most suitable government schemes.

{business_context}

AVAILABLE GOVERNMENT SCHEMES:
{''.join(schemes_summary)}

TASK:
Analyze the business comprehensively and recommend the TOP {max_results} most suitable schemes. For each recommended scheme, provide:
1. Scheme number (from the list above)
2. Match score (0-100) based on:
   - Sector alignment and relevance
   - Geographic eligibility (location match)
   - Investment amount suitability
   - Business stage and requirements
   - Subsidy/loan benefits potential
   - Eligibility criteria fit
3. 3-5 specific, actionable reasons why this scheme is recommended
4. Key benefit highlight (what makes this scheme valuable for this business)

Return your response as a JSON array with this exact structure:
[
  {{
    "scheme_number": 1,
    "match_score": 95,
    "reasons": [
      "Perfect sector match for manufacturing business",
      "Investment of ₹50 lakhs falls within scheme range",
      "35% subsidy can reduce capital burden significantly",
      "Located in eligible state with good scheme implementation",
      "Meets all eligibility criteria as new enterprise"
    ],
    "key_benefit": "Can receive up to ₹17.5 lakhs subsidy (35% of ₹50L investment)"
  }}
]

IMPORTANT: 
- Be realistic and specific with match scores
- Prioritize schemes with highest practical benefit
- Consider both eligibility AND value proposition
- Return ONLY the JSON array, no other text
- Ensure valid JSON format"""

        # Get AI recommendations
        ai_response = await ai_service.generate_content(prompt)
        
        # Parse AI response
        try:
            # Extract JSON from response
            response_text = ai_response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            ai_matches = json.loads(response_text)
            
            # Map AI recommendations to scheme objects
            matched_schemes = []
            for match in ai_matches[:max_results]:
                scheme_idx = match['scheme_number'] - 1
                if 0 <= scheme_idx < len(schemes):
                    scheme = schemes[scheme_idx]
                    matched_schemes.append({
                        'scheme': scheme,
                        'match_score': match['match_score'],
                        'reasons': match['reasons'],
                        'key_benefit': match.get('key_benefit', '')
                    })
            
            return matched_schemes
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI Response: {ai_response[:500]}")
            # Fallback to rule-based matching
            return fallback_rule_based_matching(form_data, schemes, max_results)
            
    except Exception as e:
        logger.error(f"AI matching failed: {e}")
        # Fallback to rule-based matching
        return fallback_rule_based_matching(form_data, schemes, max_results)


def fallback_rule_based_matching(form_data: dict, schemes: List[dict], max_results: int) -> List[dict]:
    """Fallback to simple rule-based matching if AI fails"""
    matched_schemes = []
    
    for scheme in schemes:
        score, reasons = calculate_match_score(scheme, form_data)
        if score > 0:
            matched_schemes.append({
                'scheme': scheme,
                'match_score': score,
                'reasons': reasons,
                'key_benefit': f"{scheme.get('schemeType', 'Scheme')} opportunity"
            })
    
    # Sort by score and return top matches
    matched_schemes.sort(key=lambda x: x['match_score'], reverse=True)
    return matched_schemes[:max_results]


def calculate_match_score(scheme: dict, form_data: dict) -> tuple[int, List[str]]:
    """
    Calculate matching score and reasons for a scheme based on form data
    
    Returns:
        Tuple of (match_score, match_reasons)
        Match score is 0-100
    """
    score = 0
    reasons = []
    
    # Extract form data
    business_sector = form_data.get("business_details", {}).get("sector", "").lower()
    business_state = form_data.get("business_details", {}).get("location", "").lower()
    total_investment = float(form_data.get("financial_details", {}).get("total_investment_amount", 0))
    
    # Sector matching (40 points)
    eligible_sectors = [s.lower() for s in scheme.get("eligibleSectors", [])]
    if "all" in eligible_sectors or "all sectors" in eligible_sectors:
        score += 40
        reasons.append("Available for all sectors")
    elif any(sector in business_sector or business_sector in sector for sector in eligible_sectors):
        score += 40
        reasons.append(f"Matches sector: {business_sector}")
    elif eligible_sectors:
        score += 10  # Partial match for having defined sectors
        
    # State matching (30 points)
    eligible_states = [s.lower() for s in scheme.get("eligibleStates", [])]
    if "all" in eligible_states or "all states" in eligible_states or "pan india" in eligible_states:
        score += 30
        reasons.append("Available across all states")
    elif any(state in business_state or business_state in state for state in eligible_states):
        score += 30
        reasons.append(f"Matches state: {business_state}")
    elif eligible_states:
        score += 5  # Partial match for having defined states
    
    # Investment range matching (30 points)
    min_investment = float(scheme.get("minInvestment", 0)) if scheme.get("minInvestment") else 0
    max_investment = float(scheme.get("maxInvestment", 0)) if scheme.get("maxInvestment") else float('inf')
    
    if min_investment <= total_investment <= max_investment:
        score += 30
        if min_investment > 0 or max_investment < float('inf'):
            reasons.append(f"Investment ₹{total_investment:,.0f} within range ₹{min_investment:,.0f} - ₹{max_investment:,.0f}")
        else:
            reasons.append("No investment restrictions")
    elif max_investment == 0:  # No max limit specified
        score += 15
        reasons.append("No upper investment limit")
    
    # Add scheme type information
    scheme_type = scheme.get("schemeType", "")
    if scheme_type:
        reasons.insert(0, f"Type: {scheme_type}")
    
    return score, reasons


@router.post("/match/{form_id}", response_model=SchemeMatchResponse)
async def match_government_schemes(
    form_id: int,
    request: SchemeMatchRequest = SchemeMatchRequest(),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Match government schemes based on form data
    
    - **form_id**: ID of the DPR form
    - **max_results**: Maximum number of matching schemes to return (default: 10)
    
    Returns a list of matched government schemes ranked by relevance
    """
    try:
        # Ensure Prisma is connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Verify form exists and belongs to current user
        form = await prisma.dprform.find_unique(
            where={"id": form_id},
            include={
                "businessDetails": True,
                "financialDetails": True,
            }
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
        
        # Check if business details exist
        if not form.businessDetails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business details are required for scheme matching. Please complete the business details section first."
            )
        
        # Get all government schemes
        schemes = await prisma.scheme.find_many()
        
        if not schemes:
            logger.warning("No government schemes found in database")
            return SchemeMatchResponse(
                success=True,
                form_id=form_id,
                business_name=form.businessName,
                total_matches=0,
                matched_schemes=[],
                message="No government schemes available in the database. Please contact administrator."
            )
        
        # Prepare comprehensive form data for AI matching
        form_data = {
            "business_name": form.businessName,
            "business_details": {
                "sector": form.businessDetails.sector if form.businessDetails else "",
                "sub_sector": form.businessDetails.subSector if form.businessDetails else "",
                "legal_structure": form.businessDetails.legalStructure if form.businessDetails else "",
                "location": form.businessDetails.location if form.businessDetails else "",
                "address": form.businessDetails.address if form.businessDetails else "",
            },
            "financial_details": {
                "total_investment_amount": form.financialDetails.totalInvestmentAmount if form.financialDetails else 0,
                "land_cost": form.financialDetails.landCost if form.financialDetails else 0,
                "building_cost": form.financialDetails.buildingCost if form.financialDetails else 0,
                "machinery_cost": form.financialDetails.machineryCost if form.financialDetails else 0,
                "working_capital": form.financialDetails.workingCapital if form.financialDetails else 0,
                "own_contribution": form.financialDetails.ownContribution if form.financialDetails else 0,
                "loan_required": form.financialDetails.loanRequired if form.financialDetails else 0,
            }
        }
        
        # Convert schemes to dict format for AI processing
        schemes_dict = []
        for scheme in schemes:
            schemes_dict.append({
                "id": scheme.id,
                "schemeName": scheme.schemeName,
                "ministry": scheme.ministry,
                "schemeType": scheme.schemeType,
                "description": scheme.description,
                "subsidyPercentage": scheme.subsidyPercentage,
                "maxSubsidyAmount": scheme.maxSubsidyAmount,
                "eligibleSectors": json.loads(scheme.eligibleSectors) if isinstance(scheme.eligibleSectors, str) else scheme.eligibleSectors,
                "eligibleStates": json.loads(scheme.eligibleStates) if isinstance(scheme.eligibleStates, str) else scheme.eligibleStates,
                "minInvestment": scheme.minInvestment,
                "maxInvestment": scheme.maxInvestment,
                "eligibilityCriteria": scheme.eligibilityCriteria,
                "applicationLink": scheme.applicationLink,
            })
        
        # Use AI to match schemes
        logger.info(f"Using AI to match schemes for form {form_id}")
        ai_matched = await ai_match_schemes(form_data, schemes_dict, request.max_results)
        
        # Build response with AI-matched schemes
        matched_schemes_response = []
        for match in ai_matched:
            scheme = match['scheme']
            matched_schemes_response.append(
                SchemeResponse(
                    id=scheme['id'],
                    scheme_name=scheme['schemeName'],
                    ministry=scheme['ministry'],
                    scheme_type=scheme['schemeType'],
                    description=scheme['description'],
                    subsidy_percentage=scheme['subsidyPercentage'],
                    max_subsidy_amount=scheme['maxSubsidyAmount'],
                    eligible_sectors=scheme['eligibleSectors'],
                    eligible_states=scheme['eligibleStates'],
                    min_investment=scheme['minInvestment'],
                    max_investment=scheme['maxInvestment'],
                    eligibility_criteria=scheme['eligibilityCriteria'],
                    application_link=scheme['applicationLink'],
                    match_score=match['match_score'],
                    match_reasons=match['reasons'],
                    key_benefit=match.get('key_benefit', '')
                )
            )
        
        logger.info(f"AI matched {len(matched_schemes_response)} schemes for form {form_id}")
        
        return SchemeMatchResponse(
            success=True,
            form_id=form_id,
            business_name=form.businessName,
            total_matches=len(matched_schemes_response),
            matched_schemes=matched_schemes_response,
            message=f"AI-powered matching found {len(matched_schemes_response)} suitable scheme(s). Showing top {min(len(matched_schemes_response), request.max_results)}."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching schemes for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match government schemes: {str(e)}"
        )


@router.get("/all", response_model=List[SchemeResponse])
async def get_all_schemes(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all available government schemes
    
    Returns a list of all government schemes in the database
    """
    try:
        # Ensure Prisma is connected
        if not prisma.is_connected():
            await prisma.connect()
        
        schemes = await prisma.scheme.find_many()
        
        scheme_responses = [
            SchemeResponse(
                id=scheme.id,
                scheme_name=scheme.schemeName,
                ministry=scheme.ministry,
                scheme_type=scheme.schemeType,
                description=scheme.description,
                subsidy_percentage=scheme.subsidyPercentage,
                max_subsidy_amount=scheme.maxSubsidyAmount,
                eligible_sectors=scheme.eligibleSectors,
                eligible_states=scheme.eligibleStates,
                min_investment=scheme.minInvestment,
                max_investment=scheme.maxInvestment,
                eligibility_criteria=scheme.eligibilityCriteria,
                application_link=scheme.applicationLink,
            )
            for scheme in schemes
        ]
        
        logger.info(f"Retrieved {len(scheme_responses)} schemes for user {current_user.id}")
        return scheme_responses
        
    except Exception as e:
        logger.error(f"Error retrieving schemes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schemes: {str(e)}"
        )
