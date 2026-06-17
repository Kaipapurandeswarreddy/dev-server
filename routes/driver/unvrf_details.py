from fastapi import APIRouter, HTTPException, Depends

from utils.response import CustomResponse
from utils.requests import FcmRequest
from config.auth import verify_jwt_unvrf_driver
import repos.user_types.unverified_driver as repo

router = APIRouter()

@router.post("/fetch")
async def fetch_unverified_driver_details_route(uid: str = Depends(verify_jwt_unvrf_driver)) -> repo.UnverifiedDriver:
    return await repo.find_driver_by_id(uid)

@router.post("/location/update")
async def update_unverified_driver_location_route(request: repo.GeoJSONPoint, uid: str = Depends(verify_jwt_unvrf_driver)) -> CustomResponse:
    if await repo.update_location(uid, request):
        return CustomResponse(detail="Location updated successfully")
    raise HTTPException(400, "Location could not be updated")

@router.post("/fcm/update")
async def update_unverified_driver_fcm_route(request: FcmRequest, uid: str = Depends(verify_jwt_unvrf_driver)) -> CustomResponse:
    if await repo.update_fcm(uid, request.fcm_token):
        return CustomResponse(detail="FCM Token updated successfully")
    raise HTTPException(400, "FCM Token could not be updated")