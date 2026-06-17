from fastapi import APIRouter, HTTPException, Depends

from utils.response import CustomResponse
from utils.requests import FcmRequest
from config.auth import verify_jwt_admin
import repos.user_types.admin as admin

router = APIRouter()

@router.post("/fetch")
async def fetch_admin_details_route(uid: str = Depends(verify_jwt_admin)) -> admin.Admin:
    return await admin.find_admin_by_id(uid)

@router.post("/location/update")
async def update_admin_location_route(request: admin.GeoJSONPoint, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if await admin.update_location(uid, request):
        return CustomResponse(detail="Location updated successfully")
    raise HTTPException(400, "Location could not be updated")

@router.post("/fcm/update")
async def update_admin_fcm_route(request: FcmRequest, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if await admin.update_fcm(uid, request.fcm_token):
        return CustomResponse(detail="FCM Token updated successfully")
    raise HTTPException(400, "FCM Token could not be updated")