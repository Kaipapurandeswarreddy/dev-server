import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import repos.user_types.driver as driver
import repos.ride.model as ride
from repos.common import GeoJSONPoint
from routes.user.rides.search import notify_nearby_drivers_bg

async def main():
    load_dotenv()
    print("=== LIVE RIDE TRIGGER ===")
    
    db = driver.DB
    collection = db[driver.COLLECTION_NAME]
    
    # 1. Find the active driver
    query = {"location": {"$ne": None}}
    drv = await collection.find_one(query)
    if not drv:
        print("[Error] No active driver found. Open your driver app!")
        return
        
    driver_obj = driver.Driver(**drv)
    
    # 2. Create the mock ride with a distinctly different pickup location (Parent's Location)
    # Move the pickup significantly away from the driver's current coordinates
    parent_lat = driver_obj.location.coordinates[1] + 0.05
    parent_lon = driver_obj.location.coordinates[0] + 0.05
    
    mock_ride = ride.Ride(
        user_id="mock_user_live",
        amb_type_id=None, # Broadcast to any ambulance type
        pickup=GeoJSONPoint(type="Point", coordinates=[parent_lon, parent_lat]),
        pickup_address="Parent's House (Manual Pin)",
        drop=GeoJSONPoint(type="Point", coordinates=[driver_obj.location.coordinates[0] - 0.05, driver_obj.location.coordinates[1] - 0.05]),
        drop_address="Drop Hospital",
        distance=5000,
        amount=500.0,
        payment_mode="cash"
    )
    
    # 3. Insert into MongoDB
    inserted_id = await ride.insert_ride(ride.SEARCHING, mock_ride)
    if not inserted_id:
        print("Failed to insert mock ride.")
        return
        
    mock_ride.id = inserted_id
    
    # 4. Notify driver app
    print(f"\n[1] Live Ride Created! (ID: {inserted_id})")
    print(f"    Pickup: {mock_ride.pickup_address}")
    print(f"    Drop: {mock_ride.drop_address}")
    print("\n[2] Check your Driver App NOW and Accept the ride!")
    print("[3] Tap 'Start Ride' and verify the pickup address DOES NOT change.")
    
    asyncio.create_task(notify_nearby_drivers_bg(mock_ride))
    
    # Keep the script alive for a few seconds to let FCM dispatch
    await asyncio.sleep(5)
    print("\nFCM Dispatched. The ride is waiting for you in the app.")

if __name__ == "__main__":
    asyncio.run(main())
