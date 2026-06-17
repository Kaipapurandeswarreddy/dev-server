from fastapi import APIRouter, Depends, HTTPException
from typing import List

from repos.data.counters import get_counter
import repos.user_types.unverified_driver as driver
import repos.user_types.driver as verified
from config.auth import verify_jwt_admin
from utils.response import CustomResponse
from utils.requests import IDRequest
from config.fcm import send_fcm_notification

router = APIRouter()

@router.post("/updates/counter")
async def unvrf_drivers_update_counter(uid: str = Depends(verify_jwt_admin)) -> str:
    counter = await get_counter("unverified_drivers")
    return str(counter)

@router.post("/list", description="All details are not included")
async def list_drivers_route(uid: str = Depends(verify_jwt_admin)) -> List[driver.UnverifiedDriver]:
    return await driver.list_vrf_pending_driver()

@router.post("/list/all", description="All details are not included")
async def list_all_drivers_route(uid: str = Depends(verify_jwt_admin)) -> List[driver.UnverifiedDriver]:
    return await driver.list_all_unvrf_drivers()

@router.post("/fetch")
async def fetch_driver_details_route(request: IDRequest, uid: str = Depends(verify_jwt_admin)) -> driver.UnverifiedDriver:
    return await driver.find_driver_by_id(request.id)

@router.post("/reject")
async def reject_details_route(request: driver.RejectRequest, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if await driver.reject_request(request):
        return CustomResponse(detail="Reject successful")
    raise HTTPException(400, "Reject failed")

@router.post("/accept", description="ID is required")
async def accept_details_route(request: verified.Driver, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if not request.id:
        raise HTTPException(400, detail="ID not specified")

    if request.fcm_token:
        await send_fcm_notification(request.fcm_token, "Welcome to Ambigo! Your profile has been approved")

    if await verified.insert_driver_with_id(request):
        if await driver.delete_driver_byid(request.id):
            return CustomResponse(detail="Driver add successful")
    raise HTTPException(400, "Driver add failed")



