from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import time
import os
from repos.data.counters import CountersClass

async def insert_counters_data():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv('MONGODB_URI')
    conn = AsyncIOMotorClient(url)
    db = conn["Data"]
    clc = db["counters"]

    await clc.insert_many([
        CountersClass(name="ambulance_type", value=time.time()).model_dump(),
        CountersClass(name="hospitals", value=time.time()).model_dump(),
        CountersClass(name="unverified_drivers", value=time.time()).model_dump(),
    ])


if __name__ == "__main__":
    asyncio.run(insert_counters_data())
