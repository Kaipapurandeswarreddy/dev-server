from repos.default import *
from repos.common import *
import time

DB = get_users_database()
COLLECTION_NAME = "unverified_drivers"

"""
    Under progress & error message both null means first time entry,
    Only either of both are not null|false after first update.
"""
class UnverifiedDriver(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    mobile: str
    name: str
    under_progress: bool
    error_message: Optional[str] = None
    portrait_image: Optional[str] = None
    poi_image: Optional[str] = None
    dl_image: Optional[str] = None
    rc_image: Optional[str] = None
    amb_front: Optional[str] = None
    amb_inside: Optional[str] = None
    location: Optional[GeoJSONPoint] = None
    fcm_token: Optional[str] = None
    jwt_token: Optional[str] = None

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)


async def find_driver_by_id(uid: str) -> Optional[UnverifiedDriver]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return UnverifiedDriver(**res)
    return None

async def find_driver_by_mobile(mobile: str) -> Optional[UnverifiedDriver]:
    clc = DB[COLLECTION_NAME]
    query = {"mobile": mobile}
    res = await clc.find_one(query)
    if res:
        return UnverifiedDriver(**res)
    return None

async def list_all_unvrf_drivers() -> List[UnverifiedDriver]:
    clc = DB[COLLECTION_NAME]
    projection = {"name": 1, "mobile": 1, "location": 1, "under_progress": 1, "_id": 1}
    result = clc.find({}, projection)
    ret_list = []
    async for r in result:
        ret_list.append(UnverifiedDriver(**r))
    return ret_list


async def list_vrf_pending_driver() -> List[UnverifiedDriver]:
    clc = DB[COLLECTION_NAME]
    projection = {"name": 1, "mobile": 1, "location": 1, "under_progress": 1, "_id": 1}
    result = clc.find({"under_progress": True}, projection)
    ret_list = []
    async for r in result:
        ret_list.append(UnverifiedDriver(**r))
    return ret_list

async def insert_driver(driver: UnverifiedDriver) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], driver)

async def update_driver(uid: str, driver: UnverifiedDriver) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, driver)

async def delete_driver_byid(uid: str) -> bool:
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)

async def get_jwt(uid: str) -> Optional[str]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "jwt_token")

async def update_jwt(uid: str, token: str) -> bool:
    body = {"jwt_token": token}
    return await update_field_value(get_users_database()[COLLECTION_NAME], uid, body)

async def get_fcm(uid: str) -> Optional[str]:
    return await get_field_value(get_users_database()[COLLECTION_NAME], uid, "fcm_token")

async def update_fcm(uid: str, token: str) -> bool:
    body = {"fcm_token": token}
    return await update_field_value(get_users_database()[COLLECTION_NAME], uid, body)

async def update_location(uid: str, location: GeoJSONPoint) -> bool:
    body = {"location": location.model_dump()}
    return await update_field_value(get_users_database()[COLLECTION_NAME], uid, body)

class RejectRequest(BaseModel):
    driver_id: str
    error_message: str

async def reject_request(request: RejectRequest) -> bool:
    body = {
        "under_progress": False,
        "error_message": request.error_message,
    }
    return await update_field_value(get_users_database()[COLLECTION_NAME], request.driver_id, body)
