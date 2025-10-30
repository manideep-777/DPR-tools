"""
Analytics API Endpoints
Provides user statistics and analytics data
"""
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from middleware.auth import get_current_user, CurrentUser
from pydantic import BaseModel
from typing import Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Prisma client
prisma = Prisma()


class UserStatsResponse(BaseModel):
    """User statistics response model"""
    total_forms: int
    draft_forms: int
    completed_forms: int
    in_progress_forms: int
    total_ai_generations: int
    average_completion: float
    last_activity: Optional[str] = None


@router.get("/user-stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get statistics for the authenticated user
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        UserStatsResponse with user statistics
        
    Raises:
        401: If user not authenticated
        500: If database error occurs
    """
    try:
        # Connect to database if not connected
        if not prisma.is_connected():
            await prisma.connect()
        
        # Get all user forms
        user_forms = await prisma.dprform.find_many(
            where={"userId": current_user.id},
            order={"lastModified": "desc"}
        )
        
        # Calculate statistics
        total_forms = len(user_forms)
        draft_forms = sum(1 for form in user_forms if form.status == "draft")
        completed_forms = sum(1 for form in user_forms if form.status == "completed")
        in_progress_forms = sum(1 for form in user_forms if form.status == "in-progress")
        
        # Calculate average completion percentage
        if total_forms > 0:
            total_completion = sum(form.completionPercentage or 0 for form in user_forms)
            average_completion = round(total_completion / total_forms, 2)
        else:
            average_completion = 0.0
        
        # Get last activity timestamp
        last_activity = None
        if user_forms:
            last_activity = user_forms[0].lastModified.isoformat() if user_forms[0].lastModified else None
        
        # Count AI generations for this user
        ai_generations_count = await prisma.generatedcontent.count(
            where={
                "form": {
                    "is": {
                        "userId": current_user.id
                    }
                }
            }
        )
        
        logger.info(f"Retrieved statistics for user {current_user.id} ({current_user.email})")
        
        return UserStatsResponse(
            total_forms=total_forms,
            draft_forms=draft_forms,
            completed_forms=completed_forms,
            in_progress_forms=in_progress_forms,
            total_ai_generations=ai_generations_count,
            average_completion=average_completion,
            last_activity=last_activity
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user statistics: {str(e)}"
        )
