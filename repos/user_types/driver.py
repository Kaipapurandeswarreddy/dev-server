from repos.default import *
from repos.common import *
from repos.deletes import insert_to_deletes
from datetime import datetime, timezone, timedelta

DB = get_users_database()
COLLECTION_NAME = "drivers"

class DriverDetails(BaseModel):
    poi_image: str
    rc_number: str
    rc_image: str
    dl_number: str
    dl_image: str

class WalletDetails(BaseModel):
    account_no: str
    ifsc_code: str
    benf_name: str
    benf_id: str | None = None
    message: str | None = None

class Driver(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    mobile: str
    photo: str
    vehicle_type: str
    vehicle_registration: str
    details: Optional[DriverDetails] = None
    wallet_balance: float = 0
    wallet_details: Optional[WalletDetails] = None
    referral_code: Optional[str] = Field(default_factory=generate_referral_code)
    location: Optional[GeoJSONPoint] = None
    fcm_token: Optional[str] = None
    jwt_token: Optional[str] = None
    last_location_update: Optional[datetime] = None

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)

async def find_driver_details_byid(uid: str) -> Optional[DriverDetails]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        data = Driver(**res)
        return data.details
    return None

async def find_driver_by_id(uid: str) -> Optional[Driver]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    projection = {"details": 0}  # exclude this field
    res = await clc.find_one(query, projection)
    if res:
        return Driver(**res)
    return None

async def find_driver_by_mobile(mobile: str) -> Optional[Driver]:
    clc = DB[COLLECTION_NAME]
    query = {"mobile": mobile}
    projection = {"details": 0}
    res = await clc.find_one(query, projection)
    if res:
        return Driver(**res)
    return None

async def find_driver_by_referral_code(code: str) -> Optional[Driver]:
    clc = DB[COLLECTION_NAME]
    query = {"referral_code": code}
    projection = {"details": 0}
    res = await clc.find_one(query, projection)
    if res:
        return Driver(**res)
    return None

async def list_driver(skip: int) -> List[Driver]:
    clc = DB[COLLECTION_NAME]
    cursor = clc.find({}, {"details": 0}).sort("_id", -1).skip(skip).limit(10)
    ret_list = []
    async for r in cursor:  # Use async for to iterate over the cursor asynchronously
        ret_list.append(Driver(**r))
    return ret_list

async def list_driver_count() -> int:
    clc = DB[COLLECTION_NAME]
    return await clc.count_documents({})


async def insert_driver_with_id(driver: Driver) -> str:
    clc = DB[COLLECTION_NAME]
    value = driver.model_dump(by_alias=True)
    value["_id"] = ObjectId(value["_id"])
    res = await clc.insert_one(value)
    return str(res.inserted_id)

async def get_wallet_balance(uid: str) -> Optional[float]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "wallet_balance")

async def update_wallet_balance(uid: str, amount: float) -> bool:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    update = {"$inc": {"wallet_balance": amount}}
    res = await clc.update_one(query, update)
    return res.modified_count > 0

async def insert_driver(driver: Driver) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], driver)

async def update_driver(uid: str, driver: Driver) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, driver)

async def delete_driver_byid(uid: str) -> bool:
    data = await find_driver_by_id(uid)
    if data:
        dtls = await find_driver_details_byid(uid)
        data.details = dtls
        await insert_to_deletes("drivers", data)
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)

async def get_vehicle_type(uid: str) -> Optional[str]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "vehicle_type")

async def get_jwt(uid: str) -> Optional[str]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "jwt_token")

async def update_jwt(uid: str, token: str) -> bool:
    body = {"jwt_token": token}
    return await update_field_value(DB[COLLECTION_NAME], uid, body)

async def get_fcm(uid: str) -> Optional[str]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "fcm_token")

async def update_fcm(uid: str, token: str) -> bool:
    body = {"fcm_token": token}
    return await update_field_value(DB[COLLECTION_NAME], uid, body)

async def get_location(uid: str) -> Optional[dict]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "location")

async def update_location(uid: str, location: GeoJSONPoint) -> bool:
    body = {
        "location": location.model_dump(),
        "last_location_update": datetime.now(timezone.utc)
    }
    return await update_field_value(DB[COLLECTION_NAME], uid, body)

async def get_wallet_details(uid: str) -> Optional[WalletDetails]:
    data = await get_field_value(DB[COLLECTION_NAME], uid, "wallet_details")
    if data:
        return WalletDetails(**data)
    return None

async def update_wallet_details(uid: str, details: WalletDetails) -> bool:
    body = {"wallet_details": details.model_dump()}
    return await update_field_value(DB[COLLECTION_NAME], uid, body)

async def find_nearby_drivers(coordinates: List[float], max_distance_meters: float, vehicle_type: Optional[str] = None) -> List[Driver]:
    """
    Find verified drivers near coordinates within max_distance_meters.
    Optionally filters by vehicle_type (amb_type_id).
    """
    clc = DB[COLLECTION_NAME]
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coordinates,
                },
                "$maxDistance": max_distance_meters,
            }
        },
        "fcm_token": {"$ne": None},  # Only drivers with an FCM token
        "last_location_update": {"$gte": datetime.now(timezone.utc) - timedelta(minutes=2)} # Only drivers currently online
    }
    if vehicle_type is not None:
        query["vehicle_type"] = vehicle_type

    cursor = clc.find(query, {"details": 0})
    drivers = []
    async for doc in cursor:
        drivers.append(Driver(**doc))
    return drivers