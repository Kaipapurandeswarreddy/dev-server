from fastapi import APIRouter, HTTPException, Depends

from utils.response import CustomResponse
from utils.requests import FcmRequest
from config.auth import verify_jwt_driver
import repos.user_types.driver as driver

router = APIRouter()

@router.post("/fetch")
async def fetch_verified_driver_details_route(uid: str = Depends(verify_jwt_driver)) -> driver.Driver:
    return await driver.find_driver_by_id(uid)

@router.post("/data/fetch")
async def fetch_driver_personal_data_route(uid: str = Depends(verify_jwt_driver)) -> driver.DriverDetails:
    return await driver.find_driver_details_byid(uid)

# @router.post("/location/update")
# async def update_verified_driver_location_route(request: driver.GeoJSONPoint, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
#     if await driver.update_location(uid, request):
#         return CustomResponse(detail="Location updated successfully")
#     raise HTTPException(400, "Location could not be updated")

@router.post("/fcm/update")
async def update_verified_driver_fcm_route(request: FcmRequest, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    if await driver.update_fcm(uid, request.fcm_token):
        return CustomResponse(detail="FCM Token updated successfully")
    raise HTTPException(400, "FCM Token could not be updated")