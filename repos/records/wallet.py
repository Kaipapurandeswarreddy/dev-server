from repos.default import *
from datetime import datetime, timezone

DB = get_records_database()
COLLECTION_NAME = "wallet"

class WalletTransaction(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    driver_id: str
    zwitch_beneficiary_id: str
    amount: float
    account_no: str
    merchant_reference_id: str 
    bank_reference_no: str
    zwitch_transfer_id: str
    status: str
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


async def list_wallet_transactions(query: dict = None, skip: int = 0, limit: int = 100) -> List[WalletTransaction]:
    if query is None:
        query = {}
    clc = DB[COLLECTION_NAME]
    result = clc.find(query).sort("_id", -1).skip(skip).limit(limit)
    ret_list = []
    async for r in result:
        ret_list.append(WalletTransaction(**r))
    return ret_list

async def insert_wallet_transaction(transaction: WalletTransaction) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], transaction)

async def update_wallet_transaction_details(id: str, transaction: WalletTransaction) -> bool:
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], id, transaction)

async def find_wallet_transaction_by_transfer_id(transfer_id: str) -> Optional[WalletTransaction]:
    clc = DB[COLLECTION_NAME]
    query = {"zwitch_beneficiary_id": transfer_id}
    res = await clc.find_one(query)
    if res:
        return WalletTransaction(**res)
    return None


