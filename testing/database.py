from zoneinfo import ZoneInfo

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
load_dotenv()

from repos.ride.model import Ride, COMPLETED

DB_URL = os.getenv('MONGODB_URI')
RIDES_DB_NAME = "Rides"

async def fetch_function():
    mongo_client = AsyncIOMotorClient(DB_URL)
    db = mongo_client[RIDES_DB_NAME]
    clc = db[COMPLETED]
    res = await clc.find_one({"payment_mode": "online"})
    if res:
        ride = Ride(**res)
        ride.created_at = ride.created_at.replace(tzinfo=timezone.utc)
        print(ride.created_at.astimezone(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M %p'))

if __name__ == "__main__":
    asyncio.run(fetch_function())