from fastapi import APIRouter, HTTPException, Header, Request
from datetime import datetime, timezone
import razorpay
import os
import asyncio
import json
import repos.records.payment as payment
from routes.driver.payment import handle_driver_share_and_referral

router = APIRouter()
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

razorpay_client = razorpay.Client(
    auth=(KEY_ID, KEY_SECRET)
)

@router.post("/complete-payment")
async def razorpay_webhook_complete_payment(request: Request, x_razorpay_signature: str = Header(None)):
    body = await request.body()

    body_str = body.decode("utf-8")

    # 2. Verify Signature
    try:
        razorpay_client.utility.verify_webhook_signature(
            body_str,
            x_razorpay_signature,
            RAZORPAY_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(400, "Invalid webhook signature")

    payload = json.loads(body_str)

    event = payload.get("event")

    # 3. We only care about captured payments
    if event != "payment.captured":
        raise HTTPException(500, f"Returned with status: Ignored")

    payment_entity = payload["payload"]["payment"]["entity"]

    rzp_payment_id = payment_entity["id"]
    rzp_order_id = payment_entity["order_id"]
    amount = payment_entity["amount"] / 100
    method = payment_entity["method"]

    # 4. Finding DB payment
    data = await payment.find_payment_by_razorpay_order_id(rzp_order_id)

    if not data:
        raise HTTPException(500, f"Data Not Found with {rzp_order_id}")

    if data.paid:
        raise HTTPException(500, f"Returned with status: Paid Already")

    # 5. Mark Paid
    data.paid = True
    data.razorpay_payment_id = rzp_payment_id
    data.payment_mode = method
    data.paid_at = datetime.now(timezone.utc)

    await payment.update_payment_byid(data.id, data)
    asyncio.create_task(handle_driver_share_and_referral(data.partner_id, data.original_amount, data.payment_mode))

    return {"status": "ok"}