from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import repos.ride.model as ride
from config.auth import verify_jwt_user

router = APIRouter()

class CurrentRideResponse(BaseModel):
    found: bool
    status: Optional[str] = None
    data: Optional[ride.Ride] = None

@router.post("/fetch")
async def fetch_current_ride_router(uid: str = Depends(verify_jwt_user)) -> CurrentRideResponse:
    query = {
        "user_id": uid,
    }
    data = await ride.find_ride_by_query(ride.SEARCHING, query)
    if data:
        return CurrentRideResponse(found=True, status=ride.SEARCHING, data=data)

    data = await ride.find_ride_by_query(ride.ACCEPTED, query)
    if data:
        return CurrentRideResponse(found=True, status=ride.ACCEPTED, data=data)

    data = await ride.find_ride_by_query(ride.ONGOING, query)
    if data:
        return CurrentRideResponse(found=True, status=ride.ONGOING, data=data)

    return CurrentRideResponse(found=False)
