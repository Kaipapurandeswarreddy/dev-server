from pydantic import BaseModel, Field
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

from config.database import get_rides_database
from repos.common import GeoJSONPoint, Timing

DB = get_rides_database()

SEARCHING = "searching_rides"
ACCEPTED = "accepted_rides"
ONGOING = "ongoing_rides"
COMPLETED = "completed_rides"
CANCELLED = "cancelled_ride"

class Ride(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    amb_type_id: Optional[str]
    pickup: GeoJSONPoint
    pickup_address: dict | str
    drop: GeoJSONPoint
    drop_address: dict | str
    distance: float
    cost: Optional[float] = None
    driver_id: Optional[str] = None
    hospital_id: Optional[str] = None
    payment_id: Optional[str] = None
    payment_mode: str
    time: Optional[Timing] = None
    is_sos: bool = False

    # MongoDB TTL timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])  # Convert ObjectId to string
        super().__init__(**data)


async def find_ride_byid(ride_type: str, uid: str) -> Optional[Ride]:
    clc = DB[ride_type]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return Ride(**res)
    return None

async def find_fields_value_byid(ride_type: str, uid: str, projection: dict) -> Optional[dict]:
    clc = DB[ride_type]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query, projection)
    if res:
        return res
    return None

async def find_ride_by_query(ride_type: str, query: dict) -> Optional[Ride]:
    clc = DB[ride_type]
    res = await clc.find_one(query)
    if res:
        return Ride(**res)
    return None

async def list_rides(ride_type: str, query: dict = None, skip: int = 0, limit: int = 100) -> List[Ride]:
    if query is None:
        query = {}
    clc = DB[ride_type]
    result = clc.find(query).sort("created_at", -1).skip(skip).limit(limit)
    ret_list = []
    async for r in result:
        ret_list.append(Ride(**r))
    return ret_list

async def insert_ride(ride_type: str, ride: Ride) -> str:
    clc = DB[ride_type]
    value = ride.model_dump(by_alias=True)
    value["_id"] = ObjectId(value["_id"])
    res = await clc.insert_one(value)
    return str(res.inserted_id)

async def update_ride_byid(ride_type: str, uid: str, ride: Ride) -> bool:
    clc = DB[ride_type]
    query = {"_id": ObjectId(uid)}
    value = ride.model_dump(by_alias=True)
    value.pop('_id')
    res = await clc.update_one(query, {"$set": value})
    return res.acknowledged

async def delete_ride_byid(ride_type: str, uid: str) -> bool:
    clc = DB[ride_type]
    query = {"_id": ObjectId(uid)}
    res = await clc.delete_one(query)
    return res.deleted_count > 0

