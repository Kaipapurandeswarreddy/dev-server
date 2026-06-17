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
    print("=== POPUP TESTER (RACE CONDITION) ===")
    
    db = driver.DB
    collection = db[driver.COLLECTION_NAME]
    
    # 1. Find an active driver
    query = {
        "location": {"$ne": None}
    }
    drv = await collection.find_one(query)
    if not drv:
        print("[Error] No active driver found with a location. Please open the driver app and ensure location is on.")
        return
        
    driver_obj = driver.Driver(**drv)
    print(f"Targeting Driver Location: {driver_obj.location.coordinates}")
    
    # 2. Setup mock ride
    mock_ride = ride.Ride(
        user_id="mock_user_popup",
        amb_type_id=None,
        pickup=GeoJSONPoint(type="Point", coordinates=driver_obj.location.coordinates),
        pickup_address="Phantom Popup Test Ride",
        drop=GeoJSONPoint(type="Point", coordinates=[driver_obj.location.coordinates[0] + 0.01, driver_obj.location.coordinates[1] + 0.01]),
        drop_address="Nowhere",
        distance=500,
        amount=50.0,
        payment_mode="cash"
    )
    
    # 3. Insert into MongoDB
    inserted_id = await ride.insert_ride(ride.SEARCHING, mock_ride)
    if not inserted_id:
        print("Failed to insert mock ride.")
        return
        
    mock_ride.id = inserted_id
    
    # 4. Notify driver app via WebSocket/FCM
    print(f"\n[1] Ride injected! (ID: {inserted_id})")
    print("Check your driver app. You should see the ride 'Phantom Popup Test Ride' appear on screen.")
    asyncio.create_task(notify_nearby_drivers_bg(mock_ride))
    
    # 5. Wait a few seconds to let it render on the phone
    wait_time = 20
    print(f"\n[2] Waiting {wait_time} seconds for you to see it...")
    for i in range(wait_time, 0, -1):
        print(f"    ... {i}")
        await asyncio.sleep(1)
        
    # 6. Delete the ride (Simulating another driver taking it)
    await ride.delete_ride_byid(ride.SEARCHING, inserted_id)
    print("\n[3] RIDE DELETED!")
    print("Now, tap the 'Accept' button on your driver app. You should see the new 'Ride Already Taken' popup!")

if __name__ == "__main__":
    asyncio.run(main())
