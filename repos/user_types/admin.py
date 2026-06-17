from repos.default import *
from repos.common import *

DB = get_users_database()
COLLECTION_NAME = "admin"

class Admin(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    mobile: str
    fcm_token: Optional[str] = None
    jwt_token: Optional[str] = None
    location: Optional[GeoJSONPoint] = None

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)


async def find_admin_by_id(uid: str) -> Optional[Admin]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return Admin(**res)
    return None

async def find_admin_by_mobile(mobile: str) -> Optional[Admin]:
    clc = DB[COLLECTION_NAME]
    query = {"mobile": mobile}
    res = await clc.find_one(query)
    if res:
        return Admin(**res)
    return None

async def list_admin() -> List[Admin]:
    clc = DB[COLLECTION_NAME]
    result = clc.find()
    ret_list = []
    async for r in result:
        ret_list.append(Admin(**r))
    return ret_list

async def insert_admin(admin: Admin) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], admin)

async def update_admin(uid: str, admin: Admin) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, admin)

async def delete_admin_byid(uid: str) -> bool:
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)

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

async def update_location(uid: str, location: GeoJSONPoint) -> bool:
    body = {"location": location.model_dump()}
    return await update_field_value(DB[COLLECTION_NAME], uid, body)
