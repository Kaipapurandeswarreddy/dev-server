from bson import ObjectId
from pydantic import BaseModel

from config.database import get_deletes_database

async def insert_to_deletes(clc_name: str, obj: BaseModel) -> bool:
    db = get_deletes_database()
    clc = db[clc_name]
    value = obj.model_dump(by_alias=True)
    value["_id"] = ObjectId(value["_id"])
    res = await clc.insert_one(value)
    return res.acknowledged