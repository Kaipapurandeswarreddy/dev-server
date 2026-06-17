from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import json

from config.auth import jwt_decode_validate, VALID_API_KEYS
import repos.user_types.user as user
import repos.user_types.driver as driver
import repos.ride.model as ride

router = APIRouter()


@router.websocket("/check") # /ws/user/rides/accepted/check
async def ride_found_check_websocket(websocket: WebSocket, api_key: str, token: str, ride_id: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(user, token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            projection = {"_id": 1}
            res = await ride.find_fields_value_byid(ride.ACCEPTED, ride_id, projection)
            if res:
                await websocket.send_text("Ride found") # Use to redirect on driver accept
                await websocket.close()
                break
                
            # If not accepted, check if it timed out in SEARCHING
            search_proj = {"timed_out": 1, "available_types": 1}
            search_res = await ride.find_fields_value_byid(ride.SEARCHING, ride_id, search_proj)
            if search_res and search_res.get("timed_out"):
                # Send the timeout payload
                timeout_payload = {
                    "status": "timeout",
                    "available_types": search_res.get("available_types", [])
                }
                await websocket.send_text(json.dumps(timeout_payload))
                await websocket.close()
                
                # Delete the ride from SEARCHING so it doesn't clutter DB
                await ride.delete_ride_byid(ride.SEARCHING, ride_id)
                break
    except WebSocketDisconnect:
        pass


@router.websocket("/driver/location") # /ws/user/rides/accepted/driver/location
async def accepted_driver_location_websocket(websocket: WebSocket, api_key: str, token: str, ride_id: str):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")
    uid = await jwt_decode_validate(user, token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            projection = {"driver_id": 1, "_id": 0}
            res = await ride.find_fields_value_byid(ride.ACCEPTED, ride_id, projection)

            if res and res.get("driver_id"):
                location = await driver.get_location(res["driver_id"])
                if location:
                    await websocket.send_text(json.dumps(location["coordinates"]))

            else:
                res = await ride.find_fields_value_byid(ride.ONGOING, ride_id, projection)
                if res:
                    await websocket.send_text("Ride started") # Use this to check if driver has started ride
                    await websocket.close()
                    break

                res = await ride.find_fields_value_byid(ride.SEARCHING, ride_id, projection)
                if res:
                    await websocket.send_text("Ride cancelled") # Use this to check if driver has cancelled ride
                    await websocket.close()
                    break
    except WebSocketDisconnect:
        pass