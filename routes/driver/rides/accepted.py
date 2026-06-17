from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

import repos.user_types.user as user
import repos.ride.model as ride
from config.auth import verify_jwt_driver
from config.fcm import send_fcm_notification
from utils.response import CustomResponse

router = APIRouter()


@router.post("/cancel")
async def cancel_accepted_ride_route(uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    query = {"driver_id": uid}
    ride_data = await ride.find_ride_by_query(ride.ACCEPTED, query)
    if not ride_data:
        raise HTTPException(400, "Ride was not cancelled")
    if not await ride.delete_ride_byid(ride.ACCEPTED, ride_data.id):
        raise HTTPException(400, "Ride was not cancelled")

    ride_data.driver_id = None
    await ride.insert_ride(ride.SEARCHING, ride_data)

    user_fcm = await user.get_fcm(ride_data.user_id)
    if user_fcm:
        await send_fcm_notification(user_fcm, "We are finding you another ride, please wait.", "Driver cancelled the ride")
    return CustomResponse(detail="Ride cancelled")

class RideStartRequest(BaseModel):
    user_otp: int | None
    pickup: ride.GeoJSONPoint
    pickup_address: str
    time: str

@router.post("/start")
async def start_accepted_ride_route(request: RideStartRequest, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    query = {"driver_id": uid}
    ride_data = await ride.find_ride_by_query(ride.ACCEPTED, query)
    if not ride_data:
        raise HTTPException(400, "Ride could not start")

    if request.user_otp is not None:
        user_otp = await user.get_field_value(user.DB[user.COLLECTION_NAME], ride_data.user_id, "otp")
        if not (user_otp and user_otp == request.user_otp):
            raise HTTPException(400, "Invalid user OTP")

    if not await ride.delete_ride_byid(ride.ACCEPTED, ride_data.id):
        raise HTTPException(400, "Ride could not start")

    # Removed the following lines so the original user's pickup isn't overwritten by the driver's device location when the ride starts
    # ride_data.pickup = request.pickup
    # ride_data.pickup_address = request.pickup_address
    ride_data.time = ride.Timing(start=request.time, end="")
    await ride.insert_ride(ride.ONGOING, ride_data)

    user_fcm = await user.get_fcm(ride_data.user_id)
    if user_fcm:
        await send_fcm_notification(user_fcm, "Ride started!!")
    return CustomResponse(detail="Ride started")

