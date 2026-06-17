import httpx
import os

KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

async def create_razorpay_order(amount: float) -> str | None:
    url = "https://api.razorpay.com/v1/orders"
    auth = (KEY_ID, KEY_SECRET)

    payload = {
        "amount": amount * 100,  # Amount in paise (₹50.00)
        "currency": "INR",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, auth=auth, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("id")
    except httpx.HTTPError as e:
        print(f"Razorpay error: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    temp = asyncio.run(create_razorpay_order(amount=500))
    print(temp)
