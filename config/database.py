from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

DB_URL = os.getenv('MONGODB_URI')

# Directly initialize the client here
mongo_client = AsyncIOMotorClient(DB_URL)

def get_data_database():
    return mongo_client["Data"]

def get_users_database():
    return mongo_client["Users"]

def get_records_database():
    return mongo_client["Records"]

def get_rides_database():
    return mongo_client["Rides"]

def get_deletes_database():
    return mongo_client["Deletes"]
