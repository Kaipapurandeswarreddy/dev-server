from repos.default import *
from datetime import datetime, timezone

from repos.user_types.driver import update_wallet_balance

DB = get_records_database()
COLLECTION_NAME = "referrals"
REFERRAL_AMOUNT = 500
TARGET_RIDES = 5

class Referral(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_type: str
    ref_from: str
    ref_to: str
    value: str
    rides_done: int = 0
    amount_recievied: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


async def process_ride_count(uid: str):
    clc = DB[COLLECTION_NAME]
    query = {"ref_to": uid}
    res = await clc.find_one(query)
    if res:
        referral = Referral(**res)
        referral.rides_done += 1
        if referral.rides_done == TARGET_RIDES:
            referral.amount_recievied = await update_wallet_balance(referral.ref_from, REFERRAL_AMOUNT)
        await update_object_in_collection_byid(DB[COLLECTION_NAME], referral.id, referral)


async def insert_referral(referral: Referral) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], referral)