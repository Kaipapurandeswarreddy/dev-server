import httpx
import os
import base64

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

AUTH_KEY = os.getenv("SMS_COUNTRY_KEY")
AUTH_TOKEN = os.getenv("SMS_COUNTRY_TOKEN")
SMS_HEADER = "AMBHPL"

from typing import Optional

def generate_otp_template(otp: str, app_signature: Optional[str] = None) -> str:
    return f"Your Ambigo verification code is: {otp}. Please do not share it with anyone else."

async def send_sms(number: str, content: str) -> bool:
    credentials = f"{AUTH_KEY}:{AUTH_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    url = f"https://restapi.smscountry.com/v0.1/Accounts/{AUTH_KEY}/SMSes/"

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
    }

    payload = {
        "Number": "91" + number,
        "Text": content,
        "SenderId": SMS_HEADER,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if not response.is_success:
                response.raise_for_status()
            return True
    except httpx.HTTPError as e:
        print(f"SMS Country error: {e}")
        return False

if __name__ == "__main__":
    text = generate_otp_template("444445")
    import asyncio
    asyncio.run(send_sms(number="7997931130", content=text))

