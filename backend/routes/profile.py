"""
User Profile API Endpoints
Handles GET and PUT operations for user profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from middleware.auth import get_current_user, CurrentUser
from models.profile_models import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateResponse
)
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User Profile"])

# Prisma client
prisma = Prisma()


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get the current user's profile
    
    Returns:
        UserProfileResponse with profile data
        
    Raises:
        404: If profile does not exist
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Retrieve profile from database
        profile = await prisma.userprofile.find_unique(
            where={"userId": current_user.id}
        )
        
        # If profile doesn't exist, create an empty one
        if profile is None:
            logger.info(f"Creating empty profile for user {current_user.id}")
            profile = await prisma.userprofile.create(
                data={
                    "userId": current_user.id
                }
            )
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.userId,
            address=profile.address,
            aadhar_number=profile.aadharNumber,
            pan_number=profile.panNumber,
            years_in_business=profile.yearsInBusiness,
            bio=profile.bio
        )
        
    except Exception as e:
        logger.error(f"Error retrieving profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/profile", response_model=ProfileUpdateResponse)
async def update_user_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update the current user's profile
    
    Args:
        profile_data: UserProfileUpdateRequest with fields to update
        
    Returns:
        ProfileUpdateResponse with updated profile
        
    Raises:
        400: If validation fails
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Check if profile exists
        existing_profile = await prisma.userprofile.find_unique(
            where={"userId": current_user.id}
        )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if profile_data.address is not None:
            update_data["address"] = profile_data.address
        if profile_data.aadhar_number is not None:
            update_data["aadharNumber"] = profile_data.aadhar_number
        if profile_data.pan_number is not None:
            update_data["panNumber"] = profile_data.pan_number
        if profile_data.years_in_business is not None:
            update_data["yearsInBusiness"] = profile_data.years_in_business
        if profile_data.bio is not None:
            update_data["bio"] = profile_data.bio
        
        # Create or update profile
        if existing_profile is None:
            # Create new profile
            logger.info(f"Creating new profile for user {current_user.id}")
            profile = await prisma.userprofile.create(
                data={
                    "userId": current_user.id,
                    **update_data
                }
            )
        else:
            # Update existing profile
            logger.info(f"Updating profile for user {current_user.id}")
            profile = await prisma.userprofile.update(
                where={"userId": current_user.id},
                data=update_data
            )
        
        return ProfileUpdateResponse(
            success=True,
            message="Profile updated successfully",
            profile=UserProfileResponse(
                id=profile.id,
                user_id=profile.userId,
                address=profile.address,
                aadhar_number=profile.aadharNumber,
                pan_number=profile.panNumber,
                years_in_business=profile.yearsInBusiness,
                bio=profile.bio
            )
        )
        
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
