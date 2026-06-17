from repos.default import *
from repos.common import *
from repos.deletes import insert_to_deletes
import random

DB = get_users_database()
COLLECTION_NAME = "users"

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    mobile: str
    otp: Optional[int] = Field(default_factory=lambda: random.randint(1000, 9999))
    referral_code: Optional[str] = Field(default_factory=generate_referral_code)
    location: Optional[GeoJSONPoint] = None
    fcm_token: Optional[str] = None
    jwt_token: Optional[str] = None

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)


async def find_user_by_id(uid: str) -> Optional[User]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return User(**res)
    return None

async def find_user_by_mobile(mobile: str) -> Optional[User]:
    clc = DB[COLLECTION_NAME]
    query = {"mobile": mobile}
    res = await clc.find_one(query)
    if res:
        return User(**res)
    return None

async def find_user_by_referral_code(code: str) -> Optional[User]:
    clc = DB[COLLECTION_NAME]
    query = {"referral_code": code}
    res = await clc.find_one(query)
    if res:
        return User(**res)
    return None

async def list_user() -> List[User]:
    clc = DB[COLLECTION_NAME]
    result = clc.find()
    ret_list = []
    async for r in result:
        ret_list.append(User(**r))
    return ret_list

async def insert_user(user: User) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], user)

async def update_user(uid: str, user: User) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, user)

async def delete_user_byid(uid: str) -> bool:
    data = await find_user_by_id(uid)
    if data:
        await insert_to_deletes("users", data)
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
