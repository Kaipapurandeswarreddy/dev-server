from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from bson import ObjectId

async def alter_data():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv('MONGODB_URI')
    conn = AsyncIOMotorClient(url)
    payments_clc = conn["Records"]["payments"]
    rides_clc = conn["Rides"]["completed_rides"]

    rides_list = rides_clc.find()
    async for ride in rides_list:
        update = { "$set" : { "partner_id": ride["driver_id"], "paid": True } }
        await payments_clc.update_one({"_id": ObjectId(ride["payment_id"])}, update)

    amb_clc = conn["Data"]["ambulance_type"]
    await amb_clc.update_many({}, {"$set": {"driver_share": 98}})


if __name__ == "__main__":
    asyncio.run(alter_data())