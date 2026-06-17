from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import asyncio
import math

from config.auth import verify_jwt_driver
import repos.records.payment as payment
from repos.user_types.driver import get_vehicle_type, update_wallet_balance
from repos.records.referrals import process_ride_count
from repos.data.ambulance_types import get_driver_share
from utils.response import CustomResponse
from utils.requests import IDRequest

router = APIRouter()


@router.post("/pending/get")
async def get_pending_payment_route(uid: str = Depends(verify_jwt_driver)) -> Optional[payment.Payment]:
    return await payment.find_pending_payment_by_partner_id(uid)


@router.post("/process")
async def process_payment_recievied_by_driver_route(request: IDRequest, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    data = await payment.find_payment_by_id(request.id)
    if not data:
        raise HTTPException(400, "Invalid payment data")
    if data.paid == True:
        raise HTTPException(400, "Payment has been completed")
    
    data.paid = True
    data.payment_mode = "cash"
    data.paid_at = datetime.now(timezone.utc)
    asyncio.run(handle_driver_share_and_referral(data.partner_id, data.original_amount, data.payment_mode))
    if await payment.update_payment_byid(data.id, data):
        return CustomResponse(detail="Payment processed successfully")
    
    raise HTTPException(400, "Payment processing failed")


async def handle_driver_share_and_referral(driver_id: str, amount: float, payment_mode: str):
    await process_ride_count(driver_id)
    amb_type_id = await get_vehicle_type(driver_id)
    driver_share = await get_driver_share(amb_type_id)

    if payment_mode == "cash":
        final_amount = -(math.floor(amount * (1 - (driver_share / 100))))
    else:
        final_amount = math.floor(amount * (driver_share / 100))
    await update_wallet_balance(driver_id, final_amount)