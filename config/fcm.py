import asyncio
import firebase_admin
from firebase_admin import credentials, messaging

import os
import json

firebase_cred_json = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_cred_json:
    cred_dict = json.loads(firebase_cred_json)
    cred = credentials.Certificate(cred_dict)
elif os.path.exists("certificates/firebase-key.json"):
    cred = credentials.Certificate("certificates/firebase-key.json")
elif os.path.exists("firebase-key.json"):
    cred = credentials.Certificate("firebase-key.json")
elif os.path.exists("/etc/secrets/firebase-key.json"):
    cred = credentials.Certificate("/etc/secrets/firebase-key.json")
else:
    raise FileNotFoundError("Firebase credentials not found!")

firebase_app = firebase_admin.initialize_app(cred)


async def send_fcm_notification(device_token: str, message: str, title: str | None = None, data: dict | None = None):
    """
    Sends an FCM notification using the Firebase Admin SDK. No errors will be raised.

    Args:
        device_token: The FCM registration token of the target device.
        message: The body of the notification.
        title: Optional title for the notification. Defaults to None.
        data: Optional dict for extra payload data.
    """

    try:
        payload_data = {
            "title": title or "New Ride Alert",
            "body": message or "",
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
        if data:
            payload_data.update({k: str(v) for k, v in data.items()})

        # For ride requests (data contains 'ride_id'), send as a data-only message to allow
        # the background service on Android to process and show custom full screen popup.
        is_data_only = False
        if data and ("ride_id" in data or data.get("data_only") == "true"):
            is_data_only = True

        notification_payload = None
        if not is_data_only:
            notification_payload = messaging.Notification(
                title=title,
                body=message,
            )

        android_notification = None
        if not is_data_only:
            android_notification = messaging.AndroidNotification(
                channel_id="high_importance_channel",
                priority="high",
                sound="default",
                default_sound=True,
            )

        message_payload = messaging.Message(
            notification=notification_payload,
            data=payload_data,
            android=messaging.AndroidConfig(
                priority="high",
                notification=android_notification,
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        content_available=True,
                    )
                )
            ),
            token=device_token,
        )
        response = await asyncio.to_thread(messaging.send, message_payload)
    except Exception as e:
        print(f"Error sending FCM notification: {e}")


if __name__ == "__main__":
    fcm_token = "d633iJtyS-ebpd7glx6Ssv:APA91bE1sDsZQyHM1F9sjrKd4Q8H7K-nPKnI5s9K_0xn3fOkCbbaX60gNfybVN74X0PORoRjglbZ3iSm7pqD-CuHDfup43VI_2-fUoNue85BDYxMY8aFRDs"
    test_title = "Test title"
    test_message = "Test body"
    asyncio.run(send_fcm_notification(fcm_token, test_title, test_message))
