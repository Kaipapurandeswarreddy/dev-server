from datetime import datetime, timezone
import os

from fastapi import APIRouter, HTTPException, Header, Request
import repos.records.wallet as wt
import repos.user_types.driver as driver
from utils.hmac_sign import generate_hmac_signature

router = APIRouter()
KEY_ID = os.getenv("ZWITCH_KEY")

@router.post("/complete-pending-transaction")
async def zwitch_webhook(request: Request, x_zwitch_signature: str = Header(None)):
    payload = await request.json()
    print(payload)
    payload_str = payload.decode("utf-8")
    if generate_hmac_signature(KEY_ID, payload_str) != x_zwitch_signature:
        raise HTTPException(400, "Invalid webhook signature")

    event = payload.get("event")
    data = payload.get("data", {})

    if event == "transfers.updated":
        transfer_id = data.get("id")
        status = data.get("status")
        bank_ref = data.get("bank_reference_number")
        error_msg = None
        if (status == "failed"):
            error_msg = data.get("reason_for_error")
        updated_at = datetime.now(timezone.utc)

        wallet_transaction: wt.WalletTransaction = await wt.find_wallet_transaction_by_transfer_id(transfer_id)
        wallet_transaction.status = status
        wallet_transaction.bank_reference_no = bank_ref
        wallet_transaction.error_message = error_msg
        wallet_transaction.updated_at = updated_at

        if not await wt.update_wallet_transaction_details(wallet_transaction.id, wallet_transaction):
            raise HTTPException(400, "Error updating wallet transaction Details")
        
    return {"status": "ok"}