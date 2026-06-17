from fastapi import APIRouter, Depends, HTTPException

from utils.response import CustomResponse
from utils.requests import FcmRequest
from config.auth import verify_jwt_user
import repos.user_types.user as user


router = APIRouter()


@router.post("/fetch", description="Fetch user details from the provided JWT Bearer token")
async def get_user_details_route(uid: str = Depends(verify_jwt_user)) -> user.User:
    return await user.find_user_by_id(uid)

@router.post("/location/update")
async def update_user_location_route(request: user.GeoJSONPoint, uid: str = Depends(verify_jwt_user)) -> CustomResponse:
    if await user.update_location(uid, request):
        return CustomResponse(detail="Location updated successfully")
    raise HTTPException(400, "Location could not be updated")

@router.post("/fcm/update")
async def update_user_fcm_route(request: FcmRequest, uid: str = Depends(verify_jwt_user)) -> CustomResponse:
    if await user.update_fcm(uid, request.fcm_token):
        return CustomResponse(detail="FCM Token updated successfully")
    raise HTTPException(400, "FCM Token could not be updated")