from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

import repos.user_types.driver as driver
from config.auth import jwt_decode_validate, VALID_API_KEYS

router = APIRouter()


@router.websocket("/update") # /ws/driver/location/update
async def update_driver_location_websocket(websocket: WebSocket, api_key: str, token: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(driver, token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            longitude, latitude = map(float, data.split(","))
            await driver.update_location(uid, driver.GeoJSONPoint(coordinates=[longitude, latitude]))
    except WebSocketDisconnect:
        pass