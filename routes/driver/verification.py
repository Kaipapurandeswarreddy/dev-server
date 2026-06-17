from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from config.auth import verify_jwt_unvrf_driver, verify_jwt
from repos.data.counters import update_counter
import repos.user_types.driver as driver
import repos.user_types.unverified_driver as unverified_driver
from utils.response import CustomResponse

router = APIRouter()

@router.post("/check")
async def check_verification_route(uid: str = Depends(verify_jwt)) -> bool:
    driver_data = await driver.get_jwt(uid)
    if driver_data:
        return True
    driver_data = await unverified_driver.get_jwt(uid)
    if driver_data:
        return False
    raise HTTPException(400, "User not found")

class VerificationUpdateRequest(BaseModel):
    portrait_image: Optional[str] = None
    poi_image: Optional[str] = None
    dl_image: Optional[str] = None
    rc_image: Optional[str] = None
    amb_front: Optional[str] = None
    amb_inside: Optional[str] = None

@router.post("/update", description="Used for first time entry and update both. While updating only pass the parameters which need to be changed.")
async def update_verification_details(request: VerificationUpdateRequest, uid: str = Depends(verify_jwt_unvrf_driver)) -> CustomResponse:
    user = await unverified_driver.find_driver_by_id(uid)

    user.under_progress = True
    user.error_message = None
    if request.portrait_image:
        user.portrait_image = request.portrait_image
    if request.poi_image:
        user.poi_image = request.poi_image
    if request.dl_image:
        user.dl_image = request.dl_image
    if request.rc_image:
        user.rc_image = request.rc_image
    if request.amb_front:
        user.amb_front = request.amb_front
    if request.amb_inside:
        user.amb_inside = request.amb_inside

    if await unverified_driver.update_driver(user.id, user):
        await update_counter("unverified_drivers")
        return CustomResponse(detail="Details updated successfully and recheck initialized")
    raise HTTPException(400, "Driver details update failed")