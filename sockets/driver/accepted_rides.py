from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

import repos.user_types.driver as driver
import repos.ride.model as ride
from config.auth import jwt_decode_validate, VALID_API_KEYS

router = APIRouter()


@router.websocket("/status") # /ws/driver/rides/accepted/status
async def accepted_ride_status_websocket(websocket: WebSocket, api_key: str, token: str, ride_id: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(driver, token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            projection = {"_id": 1}
            res = await ride.find_fields_value_byid(ride.ACCEPTED, ride_id, projection)
            if not res:
                res = await ride.find_fields_value_byid(ride.ONGOING, ride_id, projection)
                if res:
                    await websocket.close()
                    break

                await websocket.send_text("Ride cancelled") # Use to redirect on user cancel
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass