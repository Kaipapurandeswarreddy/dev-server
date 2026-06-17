from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def create_rides_index():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv('MONGODB_URI')
    conn = AsyncIOMotorClient(url)

    rides_db = conn["Rides"]
    await rides_db["searching_rides"].create_index([('created_at', 1)], expireAfterSeconds=1500) # 25 mins TTL index
    await rides_db["searching_rides"].create_index([('pickup', '2dsphere')]) # Geospatial index

    users_db = conn["Users"]
    await users_db["auth_otp"].create_index([('created_at', 1)], expireAfterSeconds=300) # 5 mins TTL index
    await users_db["drivers"].create_index([('location', '2dsphere')]) # Geospatial index for active driver locations

if __name__ == "__main__":
    asyncio.run(create_rides_index())

# mongodump --uri="mongodb://admin:07061994Camel@34.14.219.138:27017"
# mongodump --drop
# mongorestore /uri:"mongodb://admin:07061994Camel@192.168.1.3:27017" /authenticationDatabase:admin /db:Rides dump\Rides
