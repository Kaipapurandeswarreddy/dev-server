from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from bson.objectid import ObjectId

from config.database import *


async def insert_to_collection(clc, entry: BaseModel) -> str:
    value = entry.model_dump(by_alias=True)
    value.pop("_id", "id")
    res = await clc.insert_one(value)
    return str(res.inserted_id)


async def update_object_in_collection_byid(clc, uid: str, entry: BaseModel) -> bool:
    query = {"_id": ObjectId(uid)}
    value = entry.model_dump(by_alias=True)
    value.pop('_id', "id")
    res = await clc.update_one(query, {"$set": value})
    return res.acknowledged


async def delete_object_in_collection_byid(clc, uid: str) -> bool:
    query = {"_id": ObjectId(uid)}
    res = await clc.delete_one(query)
    return res.acknowledged


async def get_field_value(clc, uid: str, field: str):
    query = {"_id": ObjectId(uid)}
    projection = {field: 1, "_id": 0}
    res = await clc.find_one(query, projection)
    if res:
        return res.get(field)
    return None

async def update_field_value(clc, uid: str, data: dict) -> bool:
    query = {"_id": ObjectId(uid)}
    res = await clc.update_one(query, {"$set": data})
    return res.acknowledged
