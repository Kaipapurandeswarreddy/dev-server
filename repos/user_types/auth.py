import random, string
from datetime import datetime, timezone
from repos.default import *
from config.sms_api import send_sms, generate_otp_template

DB = get_users_database()
COLLECTION_NAME = "auth_otp"

class UserAuth(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    number: str
    otp: str

    # MongoDB TTL timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])  # Convert ObjectId to string
        super().__init__(**data)


async def send_otp(number: str, app_signature: Optional[str] = None) -> bool:
    clc = DB[COLLECTION_NAME]
    query = {"number": number}
    res = await clc.find_one(query)
    if res:
        auth = UserAuth(**res)
        msg = generate_otp_template(auth.otp, app_signature)
        return await send_sms(number, msg)

    otp = ''.join(random.choices(string.digits, k=6))
    entry = UserAuth(number=number, otp=otp)
    entry = entry.model_dump(by_alias=True)
    entry.pop('_id', "id")
    res = await clc.insert_one(entry)
    if res.inserted_id:
        msg = generate_otp_template(otp, app_signature)
        return await send_sms(number, msg)

    return False


async def verify_otp(number: str, otp: str) -> bool:
    clc = DB[COLLECTION_NAME]
    query = {"number": number}
    res = await clc.find_one(query)
    if res:
        auth = UserAuth(**res)
        if auth.otp == otp:
            return True
    return False
