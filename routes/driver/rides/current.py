from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import repos.ride.model as ride
import repos.records.payment as payment
from config.auth import verify_jwt_driver

router = APIRouter()

class CurrentRideResponse(BaseModel):
    found: bool
    status: Optional[str] = None
    data: Optional[ride.Ride] = None

@router.post("/fetch")
async def fetch_current_ride_router(uid: str = Depends(verify_jwt_driver)) -> CurrentRideResponse:
    query = {
        "driver_id": uid,
    }

    data = await ride.find_ride_by_query(ride.ACCEPTED, query)
    if data:
        return CurrentRideResponse(found=True, status=ride.ACCEPTED, data=data)

    data = await ride.find_ride_by_query(ride.ONGOING, query)
    if data:
        return CurrentRideResponse(found=True, status=ride.ONGOING, data=data)
    
    data = await payment.find_pending_payment_by_partner_id(uid, {"_id": 1})
    if data:
        return CurrentRideResponse(found=True, status="pending_payment")

    return CurrentRideResponse(found=False)
