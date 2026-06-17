import asyncio
from config.fcm import send_fcm_notification
import repos.user_types.admin as admin

async def test_emergency_alert():
    print("Fetching admins from database...")
    admins = await admin.list_admin()
    print(f"Found {len(admins)} admins.")
    
    sent_count = 0
    for a in admins:
        if a.fcm_token:
            print(f"Sending FCM to Admin: {a.name} ({a.mobile})")
            await send_fcm_notification(
                device_token=a.fcm_token,
                message=None,
                data={
                    "ride_id": "test_123",
                    "driver_name": "Test Driver",
                    "driver_mobile": "+919999999999",
                    "emergency_alert": "true"
                }
            )
            print("FCM dispatched!")
            sent_count += 1
        else:
            print(f"Admin {a.name} has no FCM token. Skipping.")
            
    if sent_count > 0:
        print(f"\nSuccessfully dispatched {sent_count} emergency notifications!")
    else:
        print("\nNo admins with FCM tokens found. Ensure you have logged into the Admin App at least once.")

if __name__ == "__main__":
    asyncio.run(test_emergency_alert())
