from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import datetime, timezone
import razorpay
import os
import asyncio
import json
from config.auth import verify_jwt_user
import repos.records.payment as payment
from utils.response import CustomResponse
from utils.hmac_sign import generate_hmac_signature
from routes.driver.payment import handle_driver_share_and_referral

router = APIRouter()
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

razorpay_client = razorpay.Client(
    auth=(KEY_ID, KEY_SECRET)
)

class PaymentFoundResponse(BaseModel):
    found: bool = False
    data: Optional[payment.Payment] = None

@router.post("/pending/get")
async def get_pending_payment_route(uid: str = Depends(verify_jwt_user)) -> PaymentFoundResponse:
    data = await payment.find_pending_payment_by_userid(uid)
    if data:
        return PaymentFoundResponse(found=True, data=data)
    return PaymentFoundResponse()


class ProcessPaymentRequest(BaseModel):
    payment_id: str
    rzp_payment_id: str
    rzp_signature: str

@router.post("/process")
async def process_payment_route(request: ProcessPaymentRequest, uid: str = Depends(verify_jwt_user)) -> CustomResponse:
    data = await payment.find_payment_by_id(request.payment_id)
    if not data:
        raise HTTPException(400, "Invalid payment data")

    signature = generate_hmac_signature(KEY_SECRET, f"{data.razorpay_order_id}|{request.rzp_payment_id}")
    if signature != request.rzp_signature:
        raise HTTPException(400, "Invalid payment, processing failed!")

    data.paid = True
    data.razorpay_payment_id = request.payment_id
    data.paid_at = datetime.now(timezone.utc)
    await payment.update_payment_byid(data.id, data)
    asyncio.run(handle_driver_share_and_referral(data.partner_id, data.original_amount, data.payment_mode))
    return CustomResponse(detail="Payment processed successfully")

# @router.post("/complete-payment")
# async def razorpay_webhook_complete_payment(request, x_razorpay_signature: str = Header(None)):
#     body = await request.body()
#     print(f"body: {body}")
#     body_str = body.decode("utf-8")

#     # 2. Verify Signature
#     try:
#         razorpay_client.utility.verify_webhook_signature(
#             body_str,
#             x_razorpay_signature,
#             RAZORPAY_WEBHOOK_SECRET
#         )
#     except Exception:
#         raise HTTPException(400, "Invalid webhook signature")

#     payload = json.loads(body_str)
#     print(f"payload: {payload}")
#     event = payload.get("event")

#     # 3. We only care about captured payments
#     if event != "payment.captured":
#         return {"status": "ignored"}

#     payment_entity = payload["payload"]["payment"]["entity"]

#     rzp_payment_id = payment_entity["id"]
#     rzp_order_id = payment_entity["order_id"]
#     amount = payment_entity["amount"] / 100
#     method = payment_entity["method"]

#     # 4. Finding DB payment
#     data = await payment.find_payment_by_id(rzp_order_id)
#     print(f"data: {data}")
#     if not data:
#         return {"status": "not_found"}

#     if data.paid:
#         return {"status": "already_processed"}

#     # 5. Mark Paid
#     data.paid = True
#     data.razorpay_payment_id = rzp_payment_id
#     data.payment_mode = method
#     data.paid_at = datetime.now(timezone.utc)

#     await payment.update_payment_byid(data.id, data)
#     asyncio.run(handle_driver_share_and_referral(data.partner_id, data.original_amount, data.payment_mode))

#     return {"status": "ok"}
