"""
DPR Form API Endpoints
Handles form creation, update, and retrieval operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
import json
from middleware.auth import get_current_user, CurrentUser
from models.form_models import (
    FormCreateRequest,
    FormCreateResponse,
    FormResponse,
    FormUpdateRequest,
    FormUpdateResponse,
    SectionUpdateResponse,
    EntrepreneurDetailsUpdate,
    BusinessDetailsUpdate,
    ProductDetailsUpdate,
    FinancialDetailsUpdate,
    RevenueAssumptionsUpdate,
    CostDetailsUpdate,
    StaffingDetailsUpdate,
    TimelineDetailsUpdate,
    CompleteFormResponse,
    EntrepreneurDetailsResponse,
    BusinessDetailsResponse,
    ProductDetailsResponse,
    FinancialDetailsResponse,
    RevenueAssumptionsResponse,
    CostDetailsResponse,
    StaffingDetailsResponse,
    TimelineDetailsResponse,
    FormListItem,
    UserFormsResponse,
    AIGenerationRequest,
    AIGenerationResponse,
    GeneratedSectionResponse,
    GeneratedContentListResponse
)
from typing import Union
import logging
from utils.ai_service import ai_service, AVAILABLE_SECTIONS
from datetime import datetime, timezone

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/form", tags=["DPR Forms"])

# Prisma client
prisma = Prisma()


@router.get("/user/forms", response_model=UserFormsResponse)
async def get_user_forms(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all DPR forms for the authenticated user
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        UserFormsResponse with total count and list of forms
        
    Raises:
        401: If user not authenticated
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Fetch all forms for the user, ordered by last modified (most recent first)
        user_forms = await prisma.dprform.find_many(
            where={"userId": current_user.id},
            order={"lastModified": "desc"}
        )
        
        # Map to FormListItem objects
        forms_list = [
            FormListItem(
                id=form.id,
                business_name=form.businessName,
                status=form.status,
                completion_percentage=form.completionPercentage,
                created_at=form.createdAt,
                last_modified=form.lastModified
            )
            for form in user_forms
        ]
        
        logger.info(f"Retrieved {len(forms_list)} forms for user {current_user.id} ({current_user.email})")
        
        return UserFormsResponse(
            total_forms=len(forms_list),
            forms=forms_list
        )
        
    except Exception as e:
        logger.error(f"Error retrieving forms for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user forms"
        )


@router.post("/create", response_model=FormCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    form_data: FormCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create a new DPR form for the authenticated user
    
    Args:
        form_data: FormCreateRequest with business_name
        current_user: Authenticated user from JWT token
        
    Returns:
        FormCreateResponse with new form details
        
    Raises:
        400: If validation fails
        401: If user not authenticated
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Create new DPR form
        new_form = await prisma.dprform.create(
            data={
                "userId": current_user.id,
                "businessName": form_data.business_name,
                "status": "draft",
                "completionPercentage": 0
            }
        )
        
        logger.info(f"New DPR form created: {new_form.id} for user {current_user.id} ({current_user.email})")
        
        return FormCreateResponse(
            success=True,
            message="DPR form created successfully",
            form_id=new_form.id,
            business_name=new_form.businessName,
            status=new_form.status,
            created_at=new_form.createdAt
        )
        
    except Exception as e:
        logger.error(f"Error creating DPR form for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create DPR form"
        )


@router.get("/{form_id}", response_model=FormResponse)
async def get_form(
    form_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Retrieve a DPR form by ID
    
    Args:
        form_id: ID of the form to retrieve
        current_user: Authenticated user from JWT token
        
    Returns:
        FormResponse with form data
        
    Raises:
        404: If form not found
        403: If user doesn't own the form
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Retrieve form
        form = await prisma.dprform.find_unique(
            where={"id": form_id}
        )
        
        if form is None:
            logger.warning(f"Form {form_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if user owns the form
        if form.userId != current_user.id:
            logger.warning(f"User {current_user.id} attempted to access form {form_id} owned by user {form.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this form"
            )
        
        return FormResponse(
            id=form.id,
            user_id=form.userId,
            business_name=form.businessName,
            status=form.status,
            completion_percentage=form.completionPercentage,
            created_at=form.createdAt,
            last_modified=form.lastModified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve form"
        )


@router.get("/{form_id}/complete", response_model=CompleteFormResponse)
async def get_complete_form(
    form_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Retrieve complete DPR form data including all sections
    
    This endpoint returns the main form data along with all filled sections:
    - Entrepreneur details
    - Business details
    - Product details
    - Financial details
    - Revenue assumptions
    - Cost details
    - Staffing details
    - Timeline details
    
    Sections that haven't been filled yet will be null in the response.
    
    Args:
        form_id: ID of the form to retrieve
        current_user: Authenticated user from JWT token
        
    Returns:
        CompleteFormResponse with all form data and sections
        
    Raises:
        404: If form not found
        403: If user doesn't own the form
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Retrieve form with all related sections
        form = await prisma.dprform.find_unique(
            where={"id": form_id},
            include={
                "entrepreneurDetails": True,
                "businessDetails": True,
                "productDetails": True,
                "financialDetails": True,
                "revenueAssumptions": True,
                "costDetails": True,
                "staffingDetails": True,
                "timelineDetails": True
            }
        )
        
        if form is None:
            logger.warning(f"Form {form_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if user owns the form
        if form.userId != current_user.id:
            logger.warning(f"User {current_user.id} attempted to access form {form_id} owned by user {form.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this form"
            )
        
        # Build complete response
        response_data = {
            "id": form.id,
            "user_id": form.userId,
            "business_name": form.businessName,
            "status": form.status,
            "completion_percentage": form.completionPercentage,
            "created_at": form.createdAt,
            "last_modified": form.lastModified
        }
        
        # Add entrepreneur details if exists
        if form.entrepreneurDetails:
            response_data["entrepreneur_details"] = EntrepreneurDetailsResponse(
                full_name=form.entrepreneurDetails.fullName,
                date_of_birth=form.entrepreneurDetails.dateOfBirth,
                education=form.entrepreneurDetails.education,
                years_of_experience=form.entrepreneurDetails.yearsOfExperience,
                previous_business_experience=form.entrepreneurDetails.previousBusinessExperience,
                technical_skills=form.entrepreneurDetails.technicalSkills
            )
        
        # Add business details if exists
        if form.businessDetails:
            response_data["business_details"] = BusinessDetailsResponse(
                business_name=form.businessDetails.businessName,
                sector=form.businessDetails.sector,
                sub_sector=form.businessDetails.subSector,
                legal_structure=form.businessDetails.legalStructure,
                registration_number=form.businessDetails.registrationNumber,
                location=form.businessDetails.location,
                address=form.businessDetails.address
            )
        
        # Add product details if exists
        if form.productDetails:
            response_data["product_details"] = ProductDetailsResponse(
                product_name=form.productDetails.productName,
                description=form.productDetails.description,
                key_features=form.productDetails.keyFeatures,
                target_customers=form.productDetails.targetCustomers,
                current_capacity=form.productDetails.currentCapacity,
                planned_capacity=form.productDetails.plannedCapacity,
                unique_selling_points=form.productDetails.uniqueSellingPoints,
                quality_certifications=form.productDetails.qualityCertifications
            )
        
        # Add financial details if exists
        if form.financialDetails:
            response_data["financial_details"] = FinancialDetailsResponse(
                total_investment_amount=form.financialDetails.totalInvestmentAmount,
                land_cost=form.financialDetails.landCost,
                building_cost=form.financialDetails.buildingCost,
                machinery_cost=form.financialDetails.machineryCost,
                working_capital=form.financialDetails.workingCapital,
                other_costs=form.financialDetails.otherCosts,
                own_contribution=form.financialDetails.ownContribution,
                loan_required=form.financialDetails.loanRequired
            )
        
        # Add revenue assumptions if exists
        if form.revenueAssumptions:
            response_data["revenue_assumptions"] = RevenueAssumptionsResponse(
                product_price=form.revenueAssumptions.productPrice,
                monthly_sales_quantity_year1=form.revenueAssumptions.monthlySalesQuantityYear1,
                monthly_sales_quantity_year2=form.revenueAssumptions.monthlySalesQuantityYear2,
                monthly_sales_quantity_year3=form.revenueAssumptions.monthlySalesQuantityYear3,
                growth_rate_percentage=form.revenueAssumptions.growthRatePercentage
            )
        
        # Add cost details if exists
        if form.costDetails:
            response_data["cost_details"] = CostDetailsResponse(
                raw_material_cost_monthly=form.costDetails.rawMaterialCostMonthly,
                labor_cost_monthly=form.costDetails.laborCostMonthly,
                utilities_cost_monthly=form.costDetails.utilitiesCostMonthly,
                rent_monthly=form.costDetails.rentMonthly,
                marketing_cost_monthly=form.costDetails.marketingCostMonthly,
                other_fixed_costs_monthly=form.costDetails.otherFixedCostsMonthly
            )
        
        # Add staffing details if exists
        if form.staffingDetails:
            response_data["staffing_details"] = StaffingDetailsResponse(
                total_employees=form.staffingDetails.totalEmployees,
                management_count=form.staffingDetails.managementCount,
                technical_staff_count=form.staffingDetails.technicalStaffCount,
                support_staff_count=form.staffingDetails.supportStaffCount,
                average_salary=form.staffingDetails.averageSalary
            )
        
        # Add timeline details if exists
        if form.timelineDetails:
            response_data["timeline_details"] = TimelineDetailsResponse(
                land_acquisition_months=form.timelineDetails.landAcquisitionMonths,
                construction_months=form.timelineDetails.constructionMonths,
                machinery_installation_months=form.timelineDetails.machineryInstallationMonths,
                trial_production_months=form.timelineDetails.trialProductionMonths,
                commercial_production_start_month=form.timelineDetails.commercialProductionStartMonth
            )
        
        logger.info(f"Complete form {form_id} retrieved by user {current_user.id} ({current_user.email})")
        
        return CompleteFormResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving complete form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve complete form"
        )


@router.put("/{form_id}", response_model=FormUpdateResponse)
async def update_form(
    form_id: int,
    form_data: FormUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update DPR form's basic information (business_name, status)
    
    Args:
        form_id: ID of the form to update
        form_data: FormUpdateRequest with fields to update
        current_user: Authenticated user from JWT token
        
    Returns:
        FormUpdateResponse with updated form details
        
    Raises:
        404: If form not found
        403: If user doesn't own the form
        400: If validation fails or no fields to update
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Retrieve form to check ownership
        form = await prisma.dprform.find_unique(
            where={"id": form_id}
        )
        
        if form is None:
            logger.warning(f"Form {form_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if user owns the form
        if form.userId != current_user.id:
            logger.warning(f"User {current_user.id} attempted to update form {form_id} owned by user {form.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this form"
            )
        
        # Build update data (only non-None fields)
        update_data = {}
        if form_data.business_name is not None:
            update_data["businessName"] = form_data.business_name
        if form_data.status is not None:
            update_data["status"] = form_data.status
        
        # Check if there's anything to update
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update form
        updated_form = await prisma.dprform.update(
            where={"id": form_id},
            data=update_data
        )
        
        logger.info(f"Form {form_id} updated by user {current_user.id} ({current_user.email})")
        
        return FormUpdateResponse(
            success=True,
            message="Form updated successfully",
            form_id=updated_form.id,
            business_name=updated_form.businessName,
            status=updated_form.status,
            completion_percentage=updated_form.completionPercentage,
            last_modified=updated_form.lastModified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update form"
        )


async def calculate_completion_percentage(form_id: int) -> int:
    """
    Calculate form completion percentage based on filled sections
    
    Args:
        form_id: ID of the form to calculate for
        
    Returns:
        Completion percentage (0-100)
    """
    # Total sections: 8 (entrepreneur, business, product, financial, revenue, cost, staffing, timeline)
    total_sections = 8
    completed_sections = 0
    
    # Check each section
    entrepreneur = await prisma.entrepreneurdetails.find_unique(where={"formId": form_id})
    if entrepreneur:
        completed_sections += 1
    
    business = await prisma.businessdetails.find_unique(where={"formId": form_id})
    if business:
        completed_sections += 1
    
    product = await prisma.productdetails.find_unique(where={"formId": form_id})
    if product:
        completed_sections += 1
    
    financial = await prisma.financialdetails.find_unique(where={"formId": form_id})
    if financial:
        completed_sections += 1
    
    revenue = await prisma.revenueassumptions.find_unique(where={"formId": form_id})
    if revenue:
        completed_sections += 1
    
    cost = await prisma.costdetails.find_unique(where={"formId": form_id})
    if cost:
        completed_sections += 1
    
    staffing = await prisma.staffingdetails.find_unique(where={"formId": form_id})
    if staffing:
        completed_sections += 1
    
    timeline = await prisma.timelinedetails.find_unique(where={"formId": form_id})
    if timeline:
        completed_sections += 1
    
    return int((completed_sections / total_sections) * 100)


@router.put("/{form_id}/section/{section_name}", response_model=SectionUpdateResponse)
async def update_form_section(
    form_id: int,
    section_name: str,
    section_data: dict,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update a specific section of the DPR form
    
    Allowed section names:
    - entrepreneur_details
    - business_details
    - product_details
    - financial_details
    - revenue_assumptions
    - cost_details
    - staffing_details
    - timeline_details
    
    Args:
        form_id: ID of the form to update
        section_name: Name of the section to update
        section_data: Section-specific update data
        current_user: Authenticated user from JWT token
        
    Returns:
        SectionUpdateResponse with update confirmation
        
    Raises:
        404: If form not found
        403: If user doesn't own the form
        400: If invalid section name or no fields to update
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Retrieve form to check ownership
        form = await prisma.dprform.find_unique(
            where={"id": form_id}
        )
        
        if form is None:
            logger.warning(f"Form {form_id} not found for section update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if user owns the form
        if form.userId != current_user.id:
            logger.warning(f"User {current_user.id} attempted to update section in form {form_id} owned by user {form.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this form"
            )
        
        # Map section names to handlers
        section_handlers = {
            "entrepreneur_details": (update_entrepreneur_section, EntrepreneurDetailsUpdate),
            "business_details": (update_business_section, BusinessDetailsUpdate),
            "product_details": (update_product_section, ProductDetailsUpdate),
            "financial_details": (update_financial_section, FinancialDetailsUpdate),
            "revenue_assumptions": (update_revenue_section, RevenueAssumptionsUpdate),
            "cost_details": (update_cost_section, CostDetailsUpdate),
            "staffing_details": (update_staffing_section, StaffingDetailsUpdate),
            "timeline_details": (update_timeline_section, TimelineDetailsUpdate)
        }
        
        # Validate section name
        if section_name not in section_handlers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid section name. Allowed: {', '.join(section_handlers.keys())}"
            )
        
        # Get handler and model for validation
        handler, model_class = section_handlers[section_name]
        
        # Validate and parse the section data
        try:
            validated_data = model_class(**section_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data for section '{section_name}': {str(e)}"
            )
        
        # Update the section
        await handler(form_id, validated_data)
        
        # Recalculate completion percentage
        completion_percentage = await calculate_completion_percentage(form_id)
        
        # Update form's completion percentage
        updated_form = await prisma.dprform.update(
            where={"id": form_id},
            data={"completionPercentage": completion_percentage}
        )
        
        logger.info(f"Section '{section_name}' updated for form {form_id} by user {current_user.id}")
        
        return SectionUpdateResponse(
            success=True,
            message=f"Section '{section_name}' updated successfully",
            form_id=form_id,
            section_name=section_name,
            completion_percentage=completion_percentage,
            last_modified=updated_form.lastModified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating section '{section_name}' for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update section '{section_name}'"
        )


# Section update helper functions

async def update_entrepreneur_section(form_id: int, data: EntrepreneurDetailsUpdate):
    """Update entrepreneur details section"""
    update_dict = {}
    if data.full_name is not None:
        update_dict["fullName"] = data.full_name
    if data.date_of_birth is not None:
        # Convert date to datetime for Prisma DateTime field
        update_dict["dateOfBirth"] = datetime.combine(data.date_of_birth, datetime.min.time())
    if data.education is not None:
        update_dict["education"] = data.education
    if data.years_of_experience is not None:
        update_dict["yearsOfExperience"] = data.years_of_experience
    if data.previous_business_experience is not None:
        update_dict["previousBusinessExperience"] = data.previous_business_experience
    if data.technical_skills is not None:
        update_dict["technicalSkills"] = data.technical_skills
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in entrepreneur_details"
        )
    
    # Check if section exists
    existing = await prisma.entrepreneurdetails.find_unique(where={"formId": form_id})
    
    if existing:
        # Update existing
        await prisma.entrepreneurdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        # Create new (require all mandatory fields)
        if not all([data.full_name, data.date_of_birth, data.education, data.years_of_experience is not None]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires: full_name, date_of_birth, education, years_of_experience"
            )
        await prisma.entrepreneurdetails.create(
            data={
                "formId": form_id,
                "fullName": data.full_name,
                "dateOfBirth": datetime.combine(data.date_of_birth, datetime.min.time()),
                "education": data.education,
                "yearsOfExperience": data.years_of_experience,
                "previousBusinessExperience": data.previous_business_experience,
                "technicalSkills": data.technical_skills
            }
        )


async def update_business_section(form_id: int, data: BusinessDetailsUpdate):
    """Update business details section"""
    update_dict = {}
    if data.business_name is not None:
        update_dict["businessName"] = data.business_name
    if data.sector is not None:
        update_dict["sector"] = data.sector
    if data.sub_sector is not None:
        update_dict["subSector"] = data.sub_sector
    if data.legal_structure is not None:
        update_dict["legalStructure"] = data.legal_structure
    if data.registration_number is not None:
        update_dict["registrationNumber"] = data.registration_number
    if data.location is not None:
        update_dict["location"] = data.location
    if data.address is not None:
        update_dict["address"] = data.address
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in business_details"
        )
    
    existing = await prisma.businessdetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.businessdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([data.business_name, data.sector, data.legal_structure, data.location, data.address]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires: business_name, sector, legal_structure, location, address"
            )
        await prisma.businessdetails.create(
            data={
                "formId": form_id,
                "businessName": data.business_name,
                "sector": data.sector,
                "subSector": data.sub_sector,
                "legalStructure": data.legal_structure,
                "registrationNumber": data.registration_number,
                "location": data.location,
                "address": data.address
            }
        )


async def update_product_section(form_id: int, data: ProductDetailsUpdate):
    """Update product details section"""
    update_dict = {}
    if data.product_name is not None:
        update_dict["productName"] = data.product_name
    if data.description is not None:
        update_dict["description"] = data.description
    if data.key_features is not None:
        # Ensure key_features is properly formatted for Prisma JSON field
        update_dict["keyFeatures"] = json.dumps(data.key_features) if isinstance(data.key_features, list) else data.key_features
    if data.target_customers is not None:
        update_dict["targetCustomers"] = data.target_customers
    if data.current_capacity is not None:
        update_dict["currentCapacity"] = data.current_capacity
    if data.planned_capacity is not None:
        update_dict["plannedCapacity"] = data.planned_capacity
    if data.unique_selling_points is not None:
        update_dict["uniqueSellingPoints"] = data.unique_selling_points
    if data.quality_certifications is not None:
        update_dict["qualityCertifications"] = data.quality_certifications
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in product_details"
        )
    
    existing = await prisma.productdetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.productdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([data.product_name, data.description, data.key_features, data.target_customers, data.planned_capacity is not None, data.unique_selling_points]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires: product_name, description, key_features, target_customers, planned_capacity, unique_selling_points"
            )
        await prisma.productdetails.create(
            data={
                "formId": form_id,
                "productName": data.product_name,
                "description": data.description,
                "keyFeatures": json.dumps(data.key_features) if isinstance(data.key_features, list) else data.key_features,
                "targetCustomers": data.target_customers,
                "currentCapacity": data.current_capacity,
                "plannedCapacity": data.planned_capacity,
                "uniqueSellingPoints": data.unique_selling_points,
                "qualityCertifications": data.quality_certifications
            }
        )


async def update_financial_section(form_id: int, data: FinancialDetailsUpdate):
    """Update financial details section"""
    update_dict = {}
    if data.total_investment_amount is not None:
        update_dict["totalInvestmentAmount"] = data.total_investment_amount
    if data.land_cost is not None:
        update_dict["landCost"] = data.land_cost
    if data.building_cost is not None:
        update_dict["buildingCost"] = data.building_cost
    if data.machinery_cost is not None:
        update_dict["machineryCost"] = data.machinery_cost
    if data.working_capital is not None:
        update_dict["workingCapital"] = data.working_capital
    if data.other_costs is not None:
        update_dict["otherCosts"] = data.other_costs
    if data.own_contribution is not None:
        update_dict["ownContribution"] = data.own_contribution
    if data.loan_required is not None:
        update_dict["loanRequired"] = data.loan_required
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in financial_details"
        )
    
    existing = await prisma.financialdetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.financialdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([
            data.total_investment_amount is not None, data.land_cost is not None, data.building_cost is not None,
            data.machinery_cost is not None, data.working_capital is not None, data.other_costs is not None,
            data.own_contribution is not None, data.loan_required is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires all financial fields"
            )
        await prisma.financialdetails.create(
            data={
                "formId": form_id,
                "totalInvestmentAmount": data.total_investment_amount,
                "landCost": data.land_cost,
                "buildingCost": data.building_cost,
                "machineryCost": data.machinery_cost,
                "workingCapital": data.working_capital,
                "otherCosts": data.other_costs,
                "ownContribution": data.own_contribution,
                "loanRequired": data.loan_required
            }
        )


async def update_revenue_section(form_id: int, data: RevenueAssumptionsUpdate):
    """Update revenue assumptions section"""
    update_dict = {}
    if data.product_price is not None:
        update_dict["productPrice"] = data.product_price
    if data.monthly_sales_quantity_year1 is not None:
        update_dict["monthlySalesQuantityYear1"] = data.monthly_sales_quantity_year1
    if data.monthly_sales_quantity_year2 is not None:
        update_dict["monthlySalesQuantityYear2"] = data.monthly_sales_quantity_year2
    if data.monthly_sales_quantity_year3 is not None:
        update_dict["monthlySalesQuantityYear3"] = data.monthly_sales_quantity_year3
    if data.growth_rate_percentage is not None:
        update_dict["growthRatePercentage"] = data.growth_rate_percentage
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in revenue_assumptions"
        )
    
    existing = await prisma.revenueassumptions.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.revenueassumptions.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([
            data.product_price is not None, data.monthly_sales_quantity_year1 is not None,
            data.monthly_sales_quantity_year2 is not None, data.monthly_sales_quantity_year3 is not None,
            data.growth_rate_percentage is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires all revenue assumption fields"
            )
        await prisma.revenueassumptions.create(
            data={
                "formId": form_id,
                "productPrice": data.product_price,
                "monthlySalesQuantityYear1": data.monthly_sales_quantity_year1,
                "monthlySalesQuantityYear2": data.monthly_sales_quantity_year2,
                "monthlySalesQuantityYear3": data.monthly_sales_quantity_year3,
                "growthRatePercentage": data.growth_rate_percentage
            }
        )


async def update_cost_section(form_id: int, data: CostDetailsUpdate):
    """Update cost details section"""
    update_dict = {}
    if data.raw_material_cost_monthly is not None:
        update_dict["rawMaterialCostMonthly"] = data.raw_material_cost_monthly
    if data.labor_cost_monthly is not None:
        update_dict["laborCostMonthly"] = data.labor_cost_monthly
    if data.utilities_cost_monthly is not None:
        update_dict["utilitiesCostMonthly"] = data.utilities_cost_monthly
    if data.rent_monthly is not None:
        update_dict["rentMonthly"] = data.rent_monthly
    if data.marketing_cost_monthly is not None:
        update_dict["marketingCostMonthly"] = data.marketing_cost_monthly
    if data.other_fixed_costs_monthly is not None:
        update_dict["otherFixedCostsMonthly"] = data.other_fixed_costs_monthly
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in cost_details"
        )
    
    existing = await prisma.costdetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.costdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([
            data.raw_material_cost_monthly is not None, data.labor_cost_monthly is not None,
            data.utilities_cost_monthly is not None, data.rent_monthly is not None,
            data.marketing_cost_monthly is not None, data.other_fixed_costs_monthly is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires all cost detail fields"
            )
        await prisma.costdetails.create(
            data={
                "formId": form_id,
                "rawMaterialCostMonthly": data.raw_material_cost_monthly,
                "laborCostMonthly": data.labor_cost_monthly,
                "utilitiesCostMonthly": data.utilities_cost_monthly,
                "rentMonthly": data.rent_monthly,
                "marketingCostMonthly": data.marketing_cost_monthly,
                "otherFixedCostsMonthly": data.other_fixed_costs_monthly
            }
        )


async def update_staffing_section(form_id: int, data: StaffingDetailsUpdate):
    """Update staffing details section"""
    update_dict = {}
    if data.total_employees is not None:
        update_dict["totalEmployees"] = data.total_employees
    if data.management_count is not None:
        update_dict["managementCount"] = data.management_count
    if data.technical_staff_count is not None:
        update_dict["technicalStaffCount"] = data.technical_staff_count
    if data.support_staff_count is not None:
        update_dict["supportStaffCount"] = data.support_staff_count
    if data.average_salary is not None:
        update_dict["averageSalary"] = data.average_salary
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in staffing_details"
        )
    
    existing = await prisma.staffingdetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.staffingdetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([
            data.total_employees is not None, data.management_count is not None,
            data.technical_staff_count is not None, data.support_staff_count is not None,
            data.average_salary is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires all staffing detail fields"
            )
        await prisma.staffingdetails.create(
            data={
                "formId": form_id,
                "totalEmployees": data.total_employees,
                "managementCount": data.management_count,
                "technicalStaffCount": data.technical_staff_count,
                "supportStaffCount": data.support_staff_count,
                "averageSalary": data.average_salary
            }
        )


async def update_timeline_section(form_id: int, data: TimelineDetailsUpdate):
    """Update timeline details section"""
    update_dict = {}
    if data.land_acquisition_months is not None:
        update_dict["landAcquisitionMonths"] = data.land_acquisition_months
    if data.construction_months is not None:
        update_dict["constructionMonths"] = data.construction_months
    if data.machinery_installation_months is not None:
        update_dict["machineryInstallationMonths"] = data.machinery_installation_months
    if data.trial_production_months is not None:
        update_dict["trialProductionMonths"] = data.trial_production_months
    if data.commercial_production_start_month is not None:
        update_dict["commercialProductionStartMonth"] = data.commercial_production_start_month
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update in timeline_details"
        )
    
    existing = await prisma.timelinedetails.find_unique(where={"formId": form_id})
    
    if existing:
        await prisma.timelinedetails.update(
            where={"formId": form_id},
            data=update_dict
        )
    else:
        if not all([
            data.land_acquisition_months is not None, data.construction_months is not None,
            data.machinery_installation_months is not None, data.trial_production_months is not None,
            data.commercial_production_start_month is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First-time creation requires all timeline detail fields"
            )
        await prisma.timelinedetails.create(
            data={
                "formId": form_id,
                "landAcquisitionMonths": data.land_acquisition_months,
                "constructionMonths": data.construction_months,
                "machineryInstallationMonths": data.machinery_installation_months,
                "trialProductionMonths": data.trial_production_months,
                "commercialProductionStartMonth": data.commercial_production_start_month
            }
        )


# ============================================
# AI CONTENT GENERATION ENDPOINTS
# ============================================

@router.post("/{form_id}/generate", response_model=AIGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_ai_content(
    form_id: int,
    request: AIGenerationRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Generate AI content for DPR sections using Google Gemini
    
    - **form_id**: ID of the DPR form
    - **sections**: List of sections to generate (optional, generates all if not specified)
    - **regenerate**: If True, regenerates existing content
    
    Available sections:
    - executive_summary
    - market_analysis
    - competitive_analysis
    - marketing_strategy
    - operational_plan
    - risk_analysis
    - swot_analysis
    - implementation_roadmap
    """
    try:
        # Check if AI service is available
        if not ai_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check GOOGLE_API_KEY configuration."
            )
        
        # Verify form exists and belongs to current user
        form = await prisma.dprform.find_unique(
            where={"id": form_id},
            include={
                "entrepreneurDetails": True,
                "businessDetails": True,
                "productDetails": True,
                "financialDetails": True,
                "revenueAssumptions": True,
                "costDetails": True,
                "staffingDetails": True,
                "timelineDetails": True
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
        
        # Determine which sections to generate
        sections_to_generate = request.sections if request.sections else AVAILABLE_SECTIONS
        
        # Validate section names
        invalid_sections = [s for s in sections_to_generate if s not in AVAILABLE_SECTIONS]
        if invalid_sections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid section names: {', '.join(invalid_sections)}"
            )
        
        # Check existing content if not regenerating
        if not request.regenerate:
            existing_sections = await prisma.generatedcontent.find_many(
                where={
                    "formId": form_id,
                    "sectionName": {"in": sections_to_generate}
                }
            )
            existing_section_names = {content.sectionName for content in existing_sections}
            sections_to_generate = [s for s in sections_to_generate if s not in existing_section_names]
        
        if not sections_to_generate:
            return AIGenerationResponse(
                success=True,
                message="All requested sections already exist. Use regenerate=true to regenerate.",
                form_id=form_id,
                total_sections=0,
                sections_generated=[]
            )
        
        # Prepare form data for AI service
        form_data = {
            "business_name": form.businessName,
            "entrepreneur_details": {
                "full_name": form.entrepreneurDetails.fullName if form.entrepreneurDetails else None,
                "education": form.entrepreneurDetails.education if form.entrepreneurDetails else None,
                "years_of_experience": form.entrepreneurDetails.yearsOfExperience if form.entrepreneurDetails else None,
                "previous_business_experience": form.entrepreneurDetails.previousBusinessExperience if form.entrepreneurDetails else None,
                "technical_skills": form.entrepreneurDetails.technicalSkills if form.entrepreneurDetails else None
            } if form.entrepreneurDetails else {},
            "business_details": {
                "business_name": form.businessDetails.businessName if form.businessDetails else None,
                "sector": form.businessDetails.sector if form.businessDetails else None,
                "legal_structure": form.businessDetails.legalStructure if form.businessDetails else None,
                "location": form.businessDetails.location if form.businessDetails else None,
                "address": form.businessDetails.address if form.businessDetails else None
            } if form.businessDetails else {},
            "product_details": {
                "product_name": form.productDetails.productName if form.productDetails else None,
                "description": form.productDetails.description if form.productDetails else None,
                "key_features": form.productDetails.keyFeatures if form.productDetails else [],
                "target_customers": form.productDetails.targetCustomers if form.productDetails else None,
                "planned_capacity": form.productDetails.plannedCapacity if form.productDetails else None,
                "unique_selling_points": form.productDetails.uniqueSellingPoints if form.productDetails else None,
                "quality_certifications": form.productDetails.qualityCertifications if form.productDetails else None
            } if form.productDetails else {},
            "financial_details": {
                "total_investment_amount": float(form.financialDetails.totalInvestmentAmount) if form.financialDetails else None,
                "loan_required": float(form.financialDetails.loanRequired) if form.financialDetails else None,
                "working_capital": float(form.financialDetails.workingCapital) if form.financialDetails else None
            } if form.financialDetails else {},
            "revenue_assumptions": {
                "product_price": float(form.revenueAssumptions.productPrice) if form.revenueAssumptions else None,
                "monthly_sales_quantity_year1": form.revenueAssumptions.monthlySalesQuantityYear1 if form.revenueAssumptions else None,
                "monthly_sales_quantity_year2": form.revenueAssumptions.monthlySalesQuantityYear2 if form.revenueAssumptions else None,
                "monthly_sales_quantity_year3": form.revenueAssumptions.monthlySalesQuantityYear3 if form.revenueAssumptions else None
            } if form.revenueAssumptions else {},
            "cost_details": {
                "marketing_cost_monthly": float(form.costDetails.marketingCostMonthly) if form.costDetails else None
            } if form.costDetails else {},
            "staffing_details": {
                "total_employees": form.staffingDetails.totalEmployees if form.staffingDetails else None
            } if form.staffingDetails else {},
            "timeline_details": {
                "land_acquisition_months": form.timelineDetails.landAcquisitionMonths if form.timelineDetails else None,
                "construction_months": form.timelineDetails.constructionMonths if form.timelineDetails else None,
                "machinery_installation_months": form.timelineDetails.machineryInstallationMonths if form.timelineDetails else None,
                "trial_production_months": form.timelineDetails.trialProductionMonths if form.timelineDetails else None,
                "commercial_production_start_month": form.timelineDetails.commercialProductionStartMonth if form.timelineDetails else None
            } if form.timelineDetails else {}
        }
        
        # Update form status to 'generating'
        await prisma.dprform.update(
            where={"id": form_id},
            data={"status": "generating"}
        )
        
        # Generate content for each section
        generated_sections = []
        
        for section_name in sections_to_generate:
            logger.info(f"Generating {section_name} for form {form_id}")
            
            # Generate content using AI service
            generated_text = ai_service.generate_section(section_name, form_data)
            
            if generated_text is None:
                logger.error(f"Failed to generate {section_name}")
                continue
            
            # Check if regenerating existing content
            if request.regenerate:
                existing = await prisma.generatedcontent.find_first(
                    where={
                        "formId": form_id,
                        "sectionName": section_name
                    },
                    order={"versionNumber": "desc"}
                )
                next_version = (existing.versionNumber + 1) if existing else 1
            else:
                next_version = 1
            
            # Store generated content
            content = await prisma.generatedcontent.create(
                data={
                    "formId": form_id,
                    "sectionName": section_name,
                    "generatedText": generated_text,
                    "aiModelUsed": ai_service.get_model_name(),
                    "confidenceScore": 85,  # Can be calculated based on response quality
                    "versionNumber": next_version,
                    "userEdited": False
                }
            )
            
            generated_sections.append(GeneratedSectionResponse(
                section_name=content.sectionName,
                generated_text=content.generatedText,
                ai_model_used=content.aiModelUsed,
                confidence_score=content.confidenceScore,
                version_number=content.versionNumber,
                generated_at=content.generatedAt
            ))
        
        # Update form status back to draft (or completed if all sections done)
        await prisma.dprform.update(
            where={"id": form_id},
            data={"status": "draft"}
        )
        
        logger.info(f"✅ Generated {len(generated_sections)} sections for form {form_id}")
        
        return AIGenerationResponse(
            success=True,
            message=f"AI content generated successfully for {len(generated_sections)} sections",
            form_id=form_id,
            total_sections=len(generated_sections),
            sections_generated=generated_sections
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI content for form {form_id}: {str(e)}")
        # Update form status back to draft on error
        try:
            await prisma.dprform.update(
                where={"id": form_id},
                data={"status": "draft"}
            )
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI content: {str(e)}"
        )


@router.get("/{form_id}/generated-content", response_model=GeneratedContentListResponse)
async def get_generated_content(
    form_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all AI-generated content for a specific form
    
    Returns all generated sections with their content, versions, and metadata.
    """
    try:
        # Verify form exists and belongs to current user
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
        
        # Get all generated content for the form
        generated_content = await prisma.generatedcontent.find_many(
            where={"formId": form_id},
            order={"sectionName": "asc"}
        )
        
        sections = [
            GeneratedSectionResponse(
                section_name=content.sectionName,
                generated_text=content.generatedText,
                ai_model_used=content.aiModelUsed,
                confidence_score=content.confidenceScore,
                version_number=content.versionNumber,
                generated_at=content.generatedAt
            )
            for content in generated_content
        ]
        
        return GeneratedContentListResponse(
            form_id=form_id,
            business_name=form.businessName,
            total_sections=len(sections),
            sections=sections
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving generated content for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve generated content: {str(e)}"
        )


# ============================================================
# AI CONTENT GENERATION - SINGLE SECTION
# ============================================================

@router.post("/{form_id}/generate/{section}", 
             response_model=AIGenerationResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Generate AI content for a single section",
             description="Generate AI content for one specific DPR section using Google Gemini API")
async def generate_single_section(
    form_id: int,
    section: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI content for a single DPR section
    
    This endpoint generates content for one specific section of the DPR.
    Useful for regenerating individual sections or selective content generation.
    
    Path Parameters:
    - form_id: The ID of the DPR form
    - section: The section name (e.g., 'executive_summary', 'market_analysis')
    
    Returns:
    - Generated content with metadata for the requested section
    """
    try:
        # Validate section name
        if section not in AVAILABLE_SECTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid section name: {section}. Valid sections are: {', '.join(AVAILABLE_SECTIONS)}"
            )
        
        # Verify form exists and belongs to current user
        form = await prisma.dprform.find_unique(
            where={"id": form_id},
            include={
                "entrepreneurDetails": True,
                "businessDetails": True,
                "productDetails": True,
                "financialDetails": True,
                "revenueAssumptions": True,
                "costDetails": True,
                "staffingDetails": True,
                "timelineDetails": True
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
        
        # Check if form has enough data for AI generation
        if not form.entrepreneurDetails or not form.businessDetails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form must have at least entrepreneur and business details before generating AI content"
            )
        
        logger.info(f"Generating AI content for section '{section}' in form {form_id}")
        
        # Prepare form data for AI service
        form_data = {
            "business_name": form.businessName,
            "entrepreneur_details": {
                "full_name": form.entrepreneurDetails.fullName if form.entrepreneurDetails else None,
                "education": form.entrepreneurDetails.education if form.entrepreneurDetails else None,
                "years_of_experience": form.entrepreneurDetails.yearsOfExperience if form.entrepreneurDetails else None,
                "previous_business_experience": form.entrepreneurDetails.previousBusinessExperience if form.entrepreneurDetails else None,
                "technical_skills": form.entrepreneurDetails.technicalSkills if form.entrepreneurDetails else None
            } if form.entrepreneurDetails else {},
            "business_details": {
                "business_name": form.businessDetails.businessName if form.businessDetails else None,
                "sector": form.businessDetails.sector if form.businessDetails else None,
                "legal_structure": form.businessDetails.legalStructure if form.businessDetails else None,
                "location": form.businessDetails.location if form.businessDetails else None,
                "address": form.businessDetails.address if form.businessDetails else None
            } if form.businessDetails else {},
            "product_details": {
                "product_name": form.productDetails.productName if form.productDetails else None,
                "description": form.productDetails.description if form.productDetails else None,
                "key_features": form.productDetails.keyFeatures if form.productDetails else [],
                "target_customers": form.productDetails.targetCustomers if form.productDetails else None,
                "planned_capacity": form.productDetails.plannedCapacity if form.productDetails else None,
                "unique_selling_points": form.productDetails.uniqueSellingPoints if form.productDetails else None,
                "quality_certifications": form.productDetails.qualityCertifications if form.productDetails else None
            } if form.productDetails else {},
            "financial_details": {
                "total_investment_amount": float(form.financialDetails.totalInvestmentAmount) if form.financialDetails else None,
                "loan_required": float(form.financialDetails.loanRequired) if form.financialDetails else None,
                "working_capital": float(form.financialDetails.workingCapital) if form.financialDetails else None
            } if form.financialDetails else {},
            "revenue_assumptions": {
                "product_price": float(form.revenueAssumptions.productPrice) if form.revenueAssumptions else None,
                "monthly_sales_quantity_year1": form.revenueAssumptions.monthlySalesQuantityYear1 if form.revenueAssumptions else None,
                "monthly_sales_quantity_year2": form.revenueAssumptions.monthlySalesQuantityYear2 if form.revenueAssumptions else None,
                "monthly_sales_quantity_year3": form.revenueAssumptions.monthlySalesQuantityYear3 if form.revenueAssumptions else None
            } if form.revenueAssumptions else {},
            "cost_details": {
                "marketing_cost_monthly": float(form.costDetails.marketingCostMonthly) if form.costDetails else None
            } if form.costDetails else {},
            "staffing_details": {
                "total_employees": form.staffingDetails.totalEmployees if form.staffingDetails else None
            } if form.staffingDetails else {},
            "timeline_details": {
                "land_acquisition_months": form.timelineDetails.landAcquisitionMonths if form.timelineDetails else None,
                "construction_months": form.timelineDetails.constructionMonths if form.timelineDetails else None,
                "machinery_installation_months": form.timelineDetails.machineryInstallationMonths if form.timelineDetails else None,
                "trial_production_months": form.timelineDetails.trialProductionMonths if form.timelineDetails else None,
                "commercial_production_start_month": form.timelineDetails.commercialProductionStartMonth if form.timelineDetails else None
            } if form.timelineDetails else {}
        }
        
        # Temporarily set status to 'generating'
        await prisma.dprform.update(
            where={"id": form_id},
            data={"status": "generating"}
        )
        
        try:
            # Generate content for the single section
            generated_text = ai_service.generate_section(section, form_data)
            
            if not generated_text:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate content for section: {section}"
                )
            
            # Check if this section already exists (for versioning)
            existing_content = await prisma.generatedcontent.find_first(
                where={
                    "formId": form_id,
                    "sectionName": section
                },
                order={"versionNumber": "desc"}
            )
            
            version_number = 1 if not existing_content else existing_content.versionNumber + 1
            
            # Store generated content in database
            generated_content = await prisma.generatedcontent.create(
                data={
                    "formId": form_id,
                    "sectionName": section,
                    "generatedText": generated_text,
                    "aiModelUsed": ai_service.get_model_name(),
                    "confidenceScore": 85,  # Default confidence score
                    "versionNumber": version_number,
                    "generatedAt": datetime.now(timezone.utc)
                }
            )
            
            # Create response
            section_response = GeneratedSectionResponse(
                section_name=generated_content.sectionName,
                generated_text=generated_content.generatedText,
                ai_model_used=generated_content.aiModelUsed,
                confidence_score=generated_content.confidenceScore,
                version_number=generated_content.versionNumber,
                generated_at=generated_content.generatedAt
            )
            
            logger.info(f"Successfully generated section '{section}' for form {form_id} (version {version_number})")
            
            return AIGenerationResponse(
                success=True,
                message=f"AI content generated successfully for {section}",
                form_id=form_id,
                sections_generated=[section_response],
                total_sections=1
            )
            
        finally:
            # Reset status back to 'draft'
            await prisma.dprform.update(
                where={"id": form_id},
                data={"status": "draft"}
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating single section '{section}' for form {form_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI content: {str(e)}"
        )
