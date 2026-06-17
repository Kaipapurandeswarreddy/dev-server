from repos.default import *
from datetime import datetime, timezone

DB = get_records_database()
COLLECTION_NAME = "offers"


class Offer(BaseModel):
    """
        Either offer_amount or offer_percentage should be specified
    """
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    description: str
    offer_amount: Optional[float]
    offer_percentage: Optional[float]
    max_discount: Optional[float] = None

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    @model_validator(mode="after")
    def check_offer_validity(self):
        if not self.offer_amount and not self.offer_percentage:
            raise ValueError("Either offer_amount or offer_percentage must be specified")
        return self

    def calculate_offer(self, amount: float) -> float:
        if self.offer_percentage is not None:
            discount = amount * (self.offer_percentage / 100)
            if self.max_discount is not None:
                discount = min(discount, self.max_discount)
            final_amount = amount - discount
        elif self.offer_amount is not None:
            final_amount = max(amount - self.offer_amount, 0)
        else:
            final_amount = amount
        return round(final_amount, 1)



async def find_offer_by_userid(user_id: str) -> Optional[Offer]:
    clc = DB[COLLECTION_NAME]
    query = {"user_id": user_id}
    res = await clc.find_one(query)
    if res:
        return Offer(**res)
    return None

async def insert_offer(offer: Offer) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], offer)

async def update_offer_byid(uid: str, offer: Offer) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, offer)

async def delete_offer_byid(uid: str) -> bool:
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)
