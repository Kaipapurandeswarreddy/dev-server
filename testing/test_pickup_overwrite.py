import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import repos.user_types.driver as driver
import repos.ride.model as ride
from repos.common import GeoJSONPoint
from routes.driver.rides.accepted import start_accepted_ride_route, RideStartRequest

async def main():
    load_dotenv()
    print("=== TESTING PICKUP LOCATION OVERWRITE ===")
    
    # 1. Find any driver
    db = driver.DB
    collection = db[driver.COLLECTION_NAME]
    drv = await collection.find_one({})
    if not drv:
        print("[Error] No driver found in local DB to test.")
        return
        
    driver_id = str(drv['_id'])
    
    # 2. Setup mock ACCEPTED ride with a specific MANUAL pickup address
    original_pickup_address = "MANUAL USER PIN: Hospital Entrance A"
    mock_ride = ride.Ride(
        user_id="mock_user_123",
        amb_type_id=None,
        driver_id=driver_id,
        pickup=GeoJSONPoint(type="Point", coordinates=[77.6, 14.6]),
        pickup_address=original_pickup_address,
        drop=GeoJSONPoint(type="Point", coordinates=[77.61, 14.61]),
        drop_address="Drop Address",
        distance=500,
        amount=50.0,
        payment_mode="cash"
    )
    
    inserted_id = await ride.insert_ride(ride.ACCEPTED, mock_ride)
    if not inserted_id:
        print("Failed to insert mock accepted ride.")
        return
        
    print(f"[1] Inserted ACCEPTED ride.")
    print(f"    Original Pickup Address: '{original_pickup_address}'")
    
    # 3. Simulate driver clicking "Start Ride" sending their current device location
    driver_device_address = "DRIVER DEVICE GPS: Random Street B"
    request = RideStartRequest(
        user_otp=None,
        pickup=GeoJSONPoint(type="Point", coordinates=[77.605, 14.605]),
        pickup_address=driver_device_address,
        time="2026-06-13 10:00:00"
    )
    
    print(f"\n[2] Simulating Driver clicking 'Start Ride'")
    print(f"    Driver App sends payload with address: '{driver_device_address}'")
    
    try:
        await start_accepted_ride_route(request, uid=driver_id)
        print("    API call successful.")
    except Exception as e:
        print(f"    API call failed: {e}")
        
    # 4. Fetch the ride from ONGOING collection and check the pickup address
    ongoing_ride = await ride.find_ride_byid(ride.ONGOING, inserted_id)
    if not ongoing_ride:
        print("\n[Error] Ride not found in ONGOING collection.")
        return
        
    print(f"\n[3] Ride successfully moved to ONGOING.")
    print(f"    Final Pickup Address saved in Database: '{ongoing_ride.pickup_address}'")
    
    if ongoing_ride.pickup_address == original_pickup_address:
        print("\n=== SUCCESS! ===")
        print("The backend perfectly preserved the user's manual pickup location!")
    elif ongoing_ride.pickup_address == driver_device_address:
        print("\n=== FAILED! ===")
        print("The backend still overwrote the manual pickup location with the driver's device location!")
    else:
        print("\n=== UNKNOWN! ===")
        
    # Clean up
    await ride.delete_ride_byid(ride.ONGOING, inserted_id)

if __name__ == "__main__":
    asyncio.run(main())
