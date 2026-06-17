from repos.default import *
from repos.records.offer import Offer
from datetime import datetime, timezone

DB = get_records_database()
COLLECTION_NAME = "payments"

class Payment(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    partner_id: str
    description: str
    original_amount: float
    charged_amount: float
    payment_mode: str
    paid: bool = False
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    offer: Optional[Offer] = None

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


async def find_pending_payment_by_userid(user_id: str) -> Optional[Payment]:
    clc = DB[COLLECTION_NAME]
    query = {"user_id": user_id, "paid": False}
    res = await clc.find_one(query)
    if res:
        return Payment(**res)
    return None


async def find_pending_payment_by_partner_id(partner_id: str, projection: dict = None) -> Optional[Payment]:
    if projection is None:
        projection = {}
    clc = DB[COLLECTION_NAME]
    query = {"partner_id": partner_id, "paid": False}
    res = await clc.find_one(query)
    if res:
        return Payment(**res)
    return None


async def find_payment_by_id(uid: str) -> Optional[Payment]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return Payment(**res)
    return None


async def find_payment_by_razorpay_order_id(razorpay_order_id: str) -> Optional[Payment]:
    clc = DB[COLLECTION_NAME]
    query = {"razorpay_order_id": razorpay_order_id}
    res = await clc.find_one(query)
    if res:
        return Payment(**res)
    return None


async def list_payments(query: dict = None, skip: int = 0, limit: int = 100) -> List[Payment]:
    if query is None:
        query = {}
    clc = DB[COLLECTION_NAME]
    result = clc.find(query).sort("_id", -1).skip(skip).limit(limit)
    ret_list = []
    async for r in result:
        ret_list.append(Payment(**r))
    return ret_list



async def insert_payment(payment: Payment) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], payment)

async def update_payment_byid(uid: str, payment: Payment) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, payment)

async def delete_payment_byid(uid: str) -> bool:
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)

