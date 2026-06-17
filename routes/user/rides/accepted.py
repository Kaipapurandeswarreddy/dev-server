from fastapi import APIRouter, Depends, HTTPException

from repos.user_types.driver import get_fcm
import repos.ride.model as ride
from config.auth import verify_jwt_user
from utils.response import CustomResponse
from config.fcm import send_fcm_notification

router = APIRouter()


@router.post("/cancel")
async def accepted_ride_cancel_route(uid: str = Depends(verify_jwt_user)) -> CustomResponse:
    query = {"user_id": uid}
    ride_data = await ride.find_ride_by_query(ride.ACCEPTED, query)

    if not ride_data:
        raise HTTPException(400, "No ride found")

    if await ride.delete_ride_byid(ride.ACCEPTED, ride_data.id):
        driver_fcm = await get_fcm(ride_data.driver_id)
        if driver_fcm:
            await send_fcm_notification(driver_fcm, "Ride was cancelled by user")
        return CustomResponse(detail="Ride was cancelled")

    raise HTTPException(400, "Ride was not cancelled")