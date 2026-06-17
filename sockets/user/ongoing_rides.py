from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import json

from config.auth import jwt_decode_validate, VALID_API_KEYS
import repos.user_types.user as user
import repos.user_types.driver as driver
import repos.ride.model as ride

router = APIRouter()


@router.websocket("/driver/location") # /ws/user/rides/ongoing/driver/location
async def ongoing_driver_location_websocket(websocket: WebSocket, api_key: str, token: str, ride_id: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(user, token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            projection = {"driver_id": 1, "_id": 0}
            res = await ride.find_fields_value_byid(ride.ONGOING, ride_id, projection)

            if res and res.get("driver_id"):
                location = await driver.get_location(res["driver_id"])
                if location:
                    await websocket.send_text(json.dumps(location["coordinates"]))
            else:
                await websocket.send_text("Ride finished") # Use this to check if driver has ended ride
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass