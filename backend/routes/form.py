"""
DPR Form API Endpoints
Handles form creation, update, and retrieval operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
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
    UserFormsResponse
)
from typing import Union
import logging

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
        update_dict["dateOfBirth"] = data.date_of_birth
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
                "dateOfBirth": data.date_of_birth,
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
        update_dict["keyFeatures"] = data.key_features
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
                "keyFeatures": data.key_features,
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
