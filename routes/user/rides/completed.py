from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional, List

from config.auth import verify_jwt_user
import repos.ride.model as ride
import repos.records.payment as payment
from utils.requests import RideIDRequest

router = APIRouter()


@router.post("/list")
async def list_rides_route(request: Request, uid: str = Depends(verify_jwt_user)) -> List[ride.Ride]:
    query = {"user_id": uid} if 'user' in request.url.path else {"driver_id": uid}
    rides = await ride.list_rides(ride.COMPLETED, query)
    
    hl = request.headers.get("Accept-Language", "en")
    if hl != "en" and rides:
        from utils.translation import translate_single_field
        import asyncio
        async def translate_ride(r_item):
            if hasattr(r_item, 'pickupAddress') and r_item.pickupAddress:
                r_item.pickupAddress = await translate_single_field(r_item.pickupAddress, hl)
            if hasattr(r_item, 'dropAddress') and r_item.dropAddress:
                r_item.dropAddress = await translate_single_field(r_item.dropAddress, hl)
        
        await asyncio.gather(*(translate_ride(r) for r in rides))
        
    return rides


@router.post("/payment/get")
async def get_payment_by_ride_id_route(request: RideIDRequest, uid: str = Depends(verify_jwt_user)) -> payment.Payment:
    ride_data = await ride.find_ride_byid(ride.COMPLETED, request.ride_id)
    if not ride_data:
        raise HTTPException(400, "Ride data not found")

    payment_id = ride_data.payment_id
    return await payment.find_payment_by_id(payment_id)
