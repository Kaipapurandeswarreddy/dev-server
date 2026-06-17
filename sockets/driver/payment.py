from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

import repos.user_types.driver as driver
from repos.records.payment import find_pending_payment_by_partner_id
from config.auth import jwt_decode_validate, VALID_API_KEYS

router = APIRouter()


@router.websocket("/pending/status") # /ws/driver/payment/pending/status
async def pending_payment_status_websocket(websocket: WebSocket, api_key: str, token: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(driver, token)
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            res = await find_pending_payment_by_partner_id(uid, {"_id": 1})
            if not res:
                await websocket.send_text("Payment completed") 
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass