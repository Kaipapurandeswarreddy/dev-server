from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json

from config.auth import jwt_decode_validate, verify_jwt_user
import repos.ride.model as ride
import repos.user_types.user as user
import repos.user_types.driver as driver
from utils.requests import RideIDRequest

router = APIRouter()


@router.post("/accepted/details")
async def accepted_driver_details_route(request: RideIDRequest, uid: str = Depends(verify_jwt_user)) -> driver.Driver:
    return await return_driver_data_fn(ride.ACCEPTED, request.ride_id)


@router.post("/ongoing/details")
async def ongoing_driver_details_route(request: RideIDRequest, uid: str = Depends(verify_jwt_user)) -> driver.Driver:
    return await return_driver_data_fn(ride.ONGOING, request.ride_id)


async def return_driver_data_fn(ride_type: str, ride_id: str) -> driver.Driver:
    projection = {"driver_id": 1, "_id": 0}
    res = await ride.find_fields_value_byid(ride_type, ride_id, projection)
    if not res or not res.get("driver_id"):
        raise HTTPException(400, "Ride data not found")

    driver_data = await driver.find_driver_by_id(res["driver_id"])
    if not driver_data:
        raise HTTPException(400, "Driver data not found")

    driver_data.referral_code = None
    driver_data.jwt_token = None
    driver_data.fcm_token = None
    driver_data.wallet_balance = 0
    driver_data.wallet_details = None
    return driver_data

