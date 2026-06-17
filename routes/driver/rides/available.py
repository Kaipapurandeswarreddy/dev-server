from fastapi import APIRouter, HTTPException, Depends

import repos.user_types.user as user
import repos.ride.model as ride
from config.auth import verify_jwt_driver
from utils.requests import RideIDRequest
from utils.response import CustomResponse
from config.fcm import send_fcm_notification

router = APIRouter()


@router.post("/accept")
async def accept_available_ride_route(request: RideIDRequest, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    query = { "driver_id": uid }
    data = await ride.find_ride_by_query(ride.ACCEPTED, query)
    if data:
        raise HTTPException(400, "Unexpected error occurred, please try again!")
    data = await ride.find_ride_by_query(ride.ONGOING, query)
    if data:
        raise HTTPException(400, "Unexpected error occurred, please try again!")

    ride_data = await ride.find_ride_byid(ride.SEARCHING, request.ride_id)
    if not ride_data:
        raise HTTPException(400, "Ride not available")
    if not await ride.delete_ride_byid(ride.SEARCHING, request.ride_id):
        raise HTTPException(400, "Ride not available")

    user_fcm = await user.get_fcm(ride_data.user_id)
    if user_fcm:
        await send_fcm_notification(user_fcm, "Driver will contact you shortly", "Ride found")

    ride_data.driver_id = uid
    await ride.insert_ride(ride.ACCEPTED, ride_data)
    return CustomResponse(detail="Ride accepted")

