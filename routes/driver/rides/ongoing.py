from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from typing import Optional, Tuple

import repos.records.payment as payment
import repos.records.offer as offer
import repos.user_types.user as user
import repos.ride.model as ride
from config.auth import verify_jwt_driver
from config.fcm import send_fcm_notification
from config.rzr_pay import create_razorpay_order
from routes.driver.payment import handle_driver_share_and_referral
import repos.user_types.admin as admin
import repos.user_types.driver as driver_repo
from utils.response import CustomResponse

router = APIRouter()

class RideEndRequest(BaseModel):
    drop: ride.GeoJSONPoint
    drop_address: str
    time: str
    cost: float
    distance: float

class RideEndResponse(BaseModel):
    take_cash: bool = False
    amount: Optional[float] = None

@router.post("/end")
async def end_ongoing_ride_route(request: RideEndRequest, uid: str = Depends(verify_jwt_driver)) -> RideEndResponse:
    query = {"driver_id": uid}
    ride_data = await ride.find_ride_by_query(ride.ONGOING, query)
    if not ride_data:
        raise HTTPException(400, "Ride could not end")
    if not await ride.delete_ride_byid(ride.ONGOING, ride_data.id):
        raise HTTPException(400, "Ride could not end")

    payment_id, amount = await handle_payment_and_offer(ride_data, request.cost, request.drop_address)

    ride_data.payment_id = payment_id
    ride_data.drop = request.drop
    ride_data.drop_address = request.drop_address
    ride_data.cost = request.cost
    ride_data.distance = request.distance
    ride_data.time.end = request.time
    await ride.insert_ride(ride.COMPLETED, ride_data)

    return await handle_ride_end_response(ride_data.payment_mode, amount, ride_data.user_id)

@router.post("/emergency/stopped")
async def stopped_vehicle_emergency_route(uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    query = {"driver_id": uid}
    ride_data = await ride.find_ride_by_query(ride.ONGOING, query)
    if not ride_data:
        raise HTTPException(400, "Could not find ongoing ride")
    
    driver_data = await driver_repo.find_driver_by_id(uid)
    driver_name = driver_data.name if driver_data else "Unknown"
    driver_mobile = driver_data.mobile if driver_data else "Unknown"
    
    admins = await admin.list_admin()
    for a in admins:
        if a.fcm_token:
            await send_fcm_notification(
                device_token=a.fcm_token,
                message=None,
                data={
                    "ride_id": ride_data.id,
                    "driver_name": driver_name,
                    "driver_mobile": driver_mobile,
                    "emergency_alert": "true"
                }
            )
    return CustomResponse(detail="Emergency alert sent")

async def handle_payment_and_offer(ride_data: ride.Ride, cost: float, drop_address: str) -> Tuple[str, float]:
    user_offer = await offer.find_offer_by_userid(ride_data.user_id)
    final_cost = cost
    if user_offer:
        final_cost = user_offer.calculate_offer(cost)
    ride_data.created_at = ride_data.created_at.replace(tzinfo=timezone.utc)
    payment_description = f"Charges for ride to {drop_address}, at {ride_data.created_at.astimezone(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M %p')}"
    payment_details = payment.Payment(user_id=ride_data.user_id, partner_id=ride_data.driver_id, description=payment_description, original_amount=cost, charged_amount=final_cost, payment_mode=ride_data.payment_mode, razorpay_order_id=None)
    if user_offer:
        payment_details.offer = user_offer
        await offer.delete_offer_byid(user_offer.id)
    if ride_data.payment_mode == "online":
        rzp_order_id = await create_razorpay_order(final_cost)
        payment_details.razorpay_order_id = rzp_order_id
    else: # If payment is cash
        payment_details.paid = True
        payment_details.paid_at = datetime.now(timezone.utc)
        await handle_driver_share_and_referral(payment_details.partner_id, payment_details.original_amount, "cash")
    return await payment.insert_payment(payment_details), final_cost


async def handle_ride_end_response(payment_mode: str, amount: float, user_id: str) -> RideEndResponse:
    user_fcm = await user.get_fcm(user_id)
    title = "Ride complete"

    if payment_mode == "online":
        if user_fcm:
            body = f"Complete payment of Rs.{amount} via UPI/Cards"
            await send_fcm_notification(user_fcm, body, title)
        return RideEndResponse()

    if user_fcm:
        body = f"Pay Rs.{amount} in cash to the driver"
        await send_fcm_notification(user_fcm, body, title)
    return RideEndResponse(take_cash=True, amount=amount)
