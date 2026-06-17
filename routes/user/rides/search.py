from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import math
import asyncio

from config.auth import jwt_decode_validate, verify_jwt_user
from config.fcm import send_fcm_notification
from repos.common import GeoJSONPoint
import repos.ride.model as ride
import repos.data.ambulance_types as at
import repos.user_types.driver as driver
from utils.requests import RideIDRequest
from utils.response import CustomResponse
from utils.translation import translate_field
import json

def get_en_str(address_obj):
    if isinstance(address_obj, dict):
        return address_obj.get('en_US', str(address_obj))
    return str(address_obj or "")

def get_json_str(address_obj):
    if isinstance(address_obj, dict):
        return json.dumps(address_obj)
    return str(address_obj or "")

router = APIRouter()

class RideRequest(BaseModel):
    amb_type_id: str | None
    pickup: GeoJSONPoint
    pickup_address: str
    drop: GeoJSONPoint
    drop_address: str
    distance: float
    payment_mode: str
    hospital_id: str | None = None
    is_sos: bool = False


def get_distance_km(coord1: list[float], coord2: list[float]) -> float:
    # coordinates are [longitude, latitude]
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371.0 # Radius of the earth in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


async def notify_nearby_drivers_bg(ride_obj: ride.Ride):
    try:
        if ride_obj.amb_type_id:
            # Match for a specific ambulance type
            threshold = await at.get_listing_threshold(ride_obj.amb_type_id)
            threshold = 5.0 if threshold is None else threshold
            eligible_drivers = await driver.find_nearby_drivers(
                coordinates=ride_obj.pickup.coordinates,
                max_distance_meters=threshold * 1000,
                vehicle_type=ride_obj.amb_type_id
            )
        else:
            # Match for "Book Any" requests
            amb_types = await at.list_ambulance_type()
            thresholds = {t.id: (t.listing_threshold if t.listing_threshold is not None else 5.0) for t in amb_types}
            max_threshold_km = max(thresholds.values(), default=5.0)
            drivers = await driver.find_nearby_drivers(
                coordinates=ride_obj.pickup.coordinates,
                max_distance_meters=max_threshold_km * 1000,
                vehicle_type=None
            )
            eligible_drivers = []
            for d in drivers:
                if not d.location:
                    continue
                d_threshold = thresholds.get(d.vehicle_type, 5.0)
                dist = get_distance_km(d.location.coordinates, ride_obj.pickup.coordinates)
                if dist <= d_threshold:
                    eligible_drivers.append(d)

        tasks = []
        for d in eligible_drivers:
            if d.fcm_token:
                cost_str = "0"
                if d.vehicle_type:
                    amb_type = await at.find_ambulance_type_byid(d.vehicle_type)
                    if amb_type:
                        calc_cost = at.calculate_fare(ride_obj.distance, amb_type.base_fare, amb_type.pricing_tier)
                        driver_share_cost = math.floor(calc_cost * (amb_type.driver_share / 100))
                        cost_str = str(driver_share_cost)
                        
                tasks.append(send_fcm_notification(
                    device_token=d.fcm_token,
                    title="New Ride Request Available",
                    message=f"New request near {get_en_str(ride_obj.pickup_address)}. Distance: {ride_obj.distance} km.",
                    data={
                        "ride_id": str(ride_obj.id or ""),
                        "pickup_address": get_json_str(ride_obj.pickup_address),
                        "drop_address": get_json_str(ride_obj.drop_address),
                        "distance": str(ride_obj.distance or "0"),
                        "payment_mode": str(ride_obj.payment_mode or ""),
                        "amb_type_id": str(ride_obj.amb_type_id or ""),
                        "pickup_lon": str(ride_obj.pickup.coordinates[0]),
                        "pickup_lat": str(ride_obj.pickup.coordinates[1]),
                        "drop_lon": str(ride_obj.drop.coordinates[0]),
                        "drop_lat": str(ride_obj.drop.coordinates[1]),
                        "cost": cost_str,
                        "is_sos": "true" if ride_obj.is_sos else "false",
                    }
                ))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"FCM alerts dispatched to {len(tasks)} eligible drivers.")
    except Exception as e:
        print(f"Error in background notification task: {e}")


async def expire_ride_search_bg(ride_id: str, coordinates: list[float], original_amb_type_id: str | None):
    from bson.objectid import ObjectId
    await asyncio.sleep(120)
    # Check if the ride is still SEARCHING
    query = {"_id": ObjectId(ride_id)}
    ride_data = await ride.find_ride_by_query(ride.SEARCHING, query)
    if not ride_data:
        return # already accepted or cancelled manually

    # Get available other vehicle types
    amb_types = await at.list_ambulance_type()
    thresholds = {t.id: (t.listing_threshold if t.listing_threshold is not None else 5.0) for t in amb_types}
    max_threshold_km = max(thresholds.values(), default=5.0)
    drivers = await driver.find_nearby_drivers(
        coordinates=coordinates,
        max_distance_meters=max_threshold_km * 1000,
        vehicle_type=None
    )
    
    available_amb_names = set()
    for d in drivers:
        if not d.location or not d.vehicle_type:
            continue
        if d.vehicle_type == original_amb_type_id:
            continue # Skip the one they already requested since no driver accepted it
            
        d_threshold = thresholds.get(d.vehicle_type, 5.0)
        dist = get_distance_km(d.location.coordinates, coordinates)
        if dist <= d_threshold:
            # Find the name of this ambulance type
            for t in amb_types:
                if t.id == d.vehicle_type:
                    available_amb_names.add(t.name)
                    break
                    
    # Update the ride with timeout flag and available vehicle types
    clc = ride.DB[ride.SEARCHING]
    await clc.update_one({"_id": ObjectId(ride_id)}, {"$set": {"timed_out": True, "available_types": list(available_amb_names)}})


@router.post("/start", description="amb_type_id must be specified, specify null if book any is chosen")
async def start_ride_search_route(request: RideRequest, uid: str = Depends(verify_jwt_user)) -> RideIDRequest:
    query = {"user_id": uid}
    if await ride.find_ride_by_query(ride.SEARCHING, query):
        raise HTTPException(400, "Only one ride request can be made at a moment")

    translated_pickup = await translate_field(request.pickup_address)
    translated_drop = await translate_field(request.drop_address)

    ride_obj = ride.Ride(user_id=uid, amb_type_id=request.amb_type_id, pickup=request.pickup, drop=request.drop, distance=request.distance, payment_mode=request.payment_mode, hospital_id=request.hospital_id, pickup_address=translated_pickup, drop_address=translated_drop, is_sos=request.is_sos)
    ride_id = await ride.insert_ride(ride.SEARCHING, ride_obj)
    if ride_id:
        asyncio.create_task(notify_nearby_drivers_bg(ride_obj))
        asyncio.create_task(expire_ride_search_bg(ride_id, ride_obj.pickup.coordinates, ride_obj.amb_type_id))
        return RideIDRequest(ride_id=ride_id)
    raise HTTPException(400, "Failed to start ride search")


@router.post("/cancel")
async def cancel_ride_search_route(uid: str = Depends(verify_jwt_user)) -> CustomResponse:
    query = {"user_id": uid}
    ride_data = await ride.find_ride_by_query(ride.SEARCHING, query)
    if not ride_data:
        raise HTTPException(400, "Ride was not cancelled")

    if await ride.delete_ride_byid(ride.SEARCHING, ride_data.id):
        return CustomResponse(detail="Ride search cancelled")
    raise HTTPException(400, "Ride was not cancelled")
