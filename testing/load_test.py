import sys
import os
import asyncio
import time
import random
from dotenv import load_dotenv
from bson import ObjectId

# Set python path to parent directory so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import repos.user_types.driver as driver
import repos.ride.model as ride
from repos.common import GeoJSONPoint

# Silence log warnings from Firebase during heavy load test
import logging
logging.getLogger("urllib3").setLevel(logging.WARNING)

async def run_single_load_task(idx, ride_obj):
    start = time.time()
    try:
        from routes.user.rides.search import notify_nearby_drivers_bg
        await notify_nearby_drivers_bg(ride_obj)
        elapsed = time.time() - start
        return True, elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"Task {idx} failed: {e}")
        return False, elapsed

async def main():
    load_dotenv()
    print("=== STARTING CONCURRENT LOAD TEST ===")
    
    db = driver.DB
    collection = db[driver.COLLECTION_NAME]
    
    # 1. Seed 100 mock drivers in a 10km radius
    print("Seeding 100 test drivers in MongoDB...")
    seeded_mobiles = []
    drivers_batch = []
    
    # Coordinates centered around Anantapur center
    center_lon = 77.59
    center_lat = 14.68
    
    test_amb_type_id = "661b6718da6c937ace9abf4d"
    
    # Ensure ambulance type is seeded
    amb_type_col = driver.get_data_database()["ambulance_type"]
    await amb_type_col.delete_many({"_id": ObjectId(test_amb_type_id)})
    await amb_type_col.insert_one({
        "_id": ObjectId(test_amb_type_id),
        "name": "Mock Basic Ambulance",
        "photo": "mock_photo.png",
        "helper_included": False,
        "otp_required": False,
        "listing_threshold": 10.0, # 10 km
        "base_fare": 100.0,
        "driver_share": 80.0,
        "pricing_tier": []
    })
    
    for i in range(100):
        mobile = f"9000000{i:03d}"
        seeded_mobiles.append(mobile)
        # Random offsets (~1km to ~8km)
        offset_lon = (random.random() - 0.5) * 0.1
        offset_lat = (random.random() - 0.5) * 0.1
        
        drv = driver.Driver(
            name=f"Load Driver {i}",
            mobile=mobile,
            photo="test.png",
            vehicle_type=test_amb_type_id,
            vehicle_registration=f"AP01XX{i:04d}",
            location=GeoJSONPoint(type="Point", coordinates=[center_lon + offset_lon, center_lat + offset_lat]),
            fcm_token=f"mock_token_{i}"
        )
        
        value = drv.model_dump(by_alias=True)
        value["_id"] = ObjectId(value["_id"])
        drivers_batch.append(value)
        
    await collection.delete_many({"mobile": {"$in": seeded_mobiles}})
    await collection.insert_many(drivers_batch)
    print("Successfully seeded 100 drivers in MongoDB.")
    
    # 2. Setup mock ride
    mock_ride = ride.Ride(
        user_id="mock_user_999",
        amb_type_id=test_amb_type_id,
        pickup=GeoJSONPoint(type="Point", coordinates=[center_lon, center_lat]),
        pickup_address="Anantapur Town Hall",
        drop=GeoJSONPoint(type="Point", coordinates=[center_lon + 0.05, center_lat + 0.05]),
        drop_address="Government Hospital",
        distance=8.5,
        payment_mode="cash"
    )
    
    # 3. Trigger concurrent load levels
    concurrency_levels = [10, 50, 100]
    
    for level in concurrency_levels:
        print(f"\n--- Running Load Test with Concurrency Level: {level} ---")
        
        # Warmup request
        await run_single_load_task(-1, mock_ride)
        
        start_time = time.time()
        
        # Spawn concurrent tasks
        tasks = [run_single_load_task(idx, mock_ride) for idx in range(level)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r[0])
        latencies = [r[1] for r in results]
        avg_latency = sum(latencies) / len(latencies)
        rps = level / total_time
        
        print(f"Concurrency Level: {level}")
        print(f"Total Completed: {success_count}/{level}")
        print(f"Total Time Taken: {total_time:.3f} seconds")
        print(f"Average Latency: {avg_latency * 1000:.1f} ms")
        print(f"Requests Per Second (RPS): {rps:.2f}")
        
    # 4. Cleanup
    print("\nCleaning up seeded test database resources...")
    await collection.delete_many({"mobile": {"$in": seeded_mobiles}})
    await amb_type_col.delete_many({"_id": ObjectId(test_amb_type_id)})
    print("Cleanup completed.")

if __name__ == "__main__":
    asyncio.run(main())
