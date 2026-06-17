from fastapi import APIRouter, Depends, HTTPException

from config.auth import verify_jwt
from utils.response import CustomResponse
import repos.records.feedback as feedback

router = APIRouter()

@router.post("/submit", description="Pass an empty string for user_id")
async def submit_feedback_route(request: feedback.Feedback, uid: str = Depends(verify_jwt)) -> CustomResponse:
    try:
        request.user_id = uid
        await feedback.insert_feedback(request)
        return CustomResponse(detail="Feedback submitted successfully")
    except:
        raise HTTPException(400, "Error submittting the feedback")
