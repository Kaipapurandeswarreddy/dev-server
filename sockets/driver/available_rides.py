from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import json

import repos.data.ambulance_types as at
import repos.user_types.driver as driver
import repos.ride.model as ride
from config.auth import jwt_decode_validate, VALID_API_KEYS

router = APIRouter()


@router.websocket("/list") # /ws/driver/rides/available/list
async def available_ride_list_websocket(websocket: WebSocket, api_key: str, token: str, amb_id: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(driver, token)
    await websocket.accept()
    threshold = await at.get_listing_threshold(amb_id) # km
    threshold = 5 if threshold is None else threshold
    try:
        while True:
            data = await websocket.receive_text()
            longitude, latitude = map(float, data.split(","))
            # Keep driver's database location updated dynamically
            await driver.update_location(uid, driver.GeoJSONPoint(coordinates=[longitude, latitude]))
            query = {
                "pickup": {
                    "$near": {
                        "$geometry": {
                          "type": "Point",
                          "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": threshold * 1000, # in meters
                    },
                },
                "$or": [
                    {"amb_type_id": amb_id},
                    {"amb_type_id": None}
                ]
            }
            rides_list = await ride.list_rides(ride.SEARCHING, query)
            rides_list = [x.model_dump_json(by_alias=True) for x in rides_list]
            await websocket.send_text(f"[{','.join(rides_list)}]")
    except WebSocketDisconnect:
        pass