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
    FormResponse
)
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/form", tags=["DPR Forms"])

# Prisma client
prisma = Prisma()


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
