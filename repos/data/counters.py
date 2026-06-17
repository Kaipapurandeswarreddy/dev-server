from pydantic import BaseModel
import time

from config.database import get_data_database

COLLECTION_NAME = "counters"

"""
    Established counters are:
    1) ambulance_type
    2) hospitals
    3) unverified_drivers
"""

class CountersClass(BaseModel):
    name: str
    value: float

async def update_counter(name: str):
    db = get_data_database()
    clc = db[COLLECTION_NAME]
    query = {"name": name}
    await clc.update_one(query, {"$set": {"value": time.time()}}, upsert=True)

async def get_counter(name: str) -> float:
    db = get_data_database()
    clc = db[COLLECTION_NAME]
    result = await clc.find_one({"name": name})
    if result is None:
        return 0.0
    return result["value"]