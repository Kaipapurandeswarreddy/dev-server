from fastapi import APIRouter, HTTPException, Depends

from config.auth import verify_jwt_driver
import repos.ride.model as ride
import repos.user_types.user as user
from utils.requests import RideIDRequest

router = APIRouter()


@router.post("/accepted/details")
async def accepted_user_details_route(request: RideIDRequest, uid: str = Depends(verify_jwt_driver)) -> user.User:
    return await return_user_data_fn(ride.ACCEPTED, request.ride_id)


@router.post("/ongoing/details")
async def ongoing_user_details_route(request: RideIDRequest, uid: str = Depends(verify_jwt_driver)) -> user.User:
    return await return_user_data_fn(ride.ONGOING, request.ride_id)


async def return_user_data_fn(ride_type: str, ride_id: str) -> user.User:
    projection = {"user_id": 1, "_id": 0}
    res = await ride.find_fields_value_byid(ride_type, ride_id, projection)
    if not res or not res.get("user_id"):
        raise HTTPException(400, "Ride data not found")

    user_data = await user.find_user_by_id(res["user_id"])
    if not user_data:
        raise HTTPException(400, "Driver data not found")

    user_data.otp = None
    user_data.referral_code = None
    user_data.jwt_token = None
    user_data.fcm_token = None
    return user_data

