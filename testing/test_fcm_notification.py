import sys
import os
import asyncio
from dotenv import load_dotenv

# Set python path to parent directory so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import repos.user_types.driver as driver
import repos.ride.model as ride
from repos.common import GeoJSONPoint
from bson import ObjectId

async def main():
    load_dotenv()
    print("=== Testing Driver Query Geospatial Search ===")
    
    db = driver.DB
    collection = db[driver.COLLECTION_NAME]
    
    # Check current drivers count
    count = await collection.count_documents({})
    print(f"Initial drivers in database: {count}")
    
    # 1. Seed a temporary driver for matching
    test_mobile = "9999999999"
    test_amb_type_id = "661b6718da6c937ace9abf4d"
    test_driver = driver.Driver(
        name="Test Driver",
        mobile=test_mobile,
        photo="test.png",
        vehicle_type=test_amb_type_id,
        vehicle_registration="AP01XX1234",
        location=GeoJSONPoint(type="Point", coordinates=[80.002, 13.002]), # Near test pickup coordinates
        fcm_token="mock_fcm_token_123"
    )
    
    # Remove existing driver with the same mobile just in case
    await collection.delete_many({"mobile": test_mobile})
    
    # Seed the ambulance type configuration so that the thresholds lookup works
    amb_type_col = driver.get_data_database()["ambulance_type"]
    await amb_type_col.delete_many({"_id": ObjectId(test_amb_type_id)})
    await amb_type_col.insert_one({
        "_id": ObjectId(test_amb_type_id),
        "name": "Mock Basic Ambulance",
        "photo": "mock_photo.png",
        "helper_included": False,
        "otp_required": False,
        "listing_threshold": 5.0, # 5 km threshold
        "base_fare": 100.0,
        "driver_share": 80.0,
        "pricing_tier": []
    })
    
    driver_id = await driver.insert_driver(test_driver)
    print(f"Seeded temporary test driver with ID: {driver_id}")
    
    # Use standard test coordinates: [longitude, latitude]
    test_coords = [80.0, 13.0]
    
    # Fetch drivers within 10km
    nearby = await driver.find_nearby_drivers(test_coords, 10000)
    print(f"Found {len(nearby)} drivers with FCM tokens within 10 km of {test_coords}")
    for idx, d in enumerate(nearby):
        print(f"Driver {idx+1}: {d.name} | Mobile: {d.mobile} | Location: {d.location.coordinates if d.location else None} | FCM Token: {d.fcm_token}")
        
    print("\n=== Simulating Ride Request Creation & Match ===")
    from routes.user.rides.search import notify_nearby_drivers_bg
    
    mock_ride = ride.Ride(
        user_id="mock_user_123",
        amb_type_id=test_amb_type_id,
        pickup=GeoJSONPoint(type="Point", coordinates=[80.001, 13.001]),
        pickup_address="Test Pickup St, City",
        drop=GeoJSONPoint(type="Point", coordinates=[80.05, 13.05]),
        drop_address="Test Hospital, City",
        distance=5.2,
        payment_mode="cash"
    )
    
    # Trigger background notification matcher
    await notify_nearby_drivers_bg(mock_ride)
    print("Background notification match workflow simulated successfully.")
    
    # Clean up seeded resources
    await collection.delete_many({"mobile": test_mobile})
    await amb_type_col.delete_many({"_id": ObjectId(test_amb_type_id)})
    print("Cleaned up temporary seeded resources.")

if __name__ == "__main__":
    asyncio.run(main())
