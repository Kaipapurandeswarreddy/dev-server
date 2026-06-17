import httpx
import os

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

CLI_TOKEN = os.getenv("CLOUDSHOPE_TOKEN")
CLI_NUMBER = os.getenv("CLOUDSHOPE_NUMBER")


async def initiate_call_masking(from_number: str, to_number: str) -> str:
    url = "https://apiv2.cloudshope.com/api/outboundCall"

    headers = {
        "Authorization": f"Bearer {CLI_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "from_number": from_number,
        "mobile_number": to_number,
        "cli_number" : CLI_NUMBER,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if not response.is_success:
                response.raise_for_status()
            return f"+91{CLI_NUMBER}"
    except httpx.HTTPError as e:
        print(f"Cloudshope error: {e}")
        raise "Error placing the call"
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(initiate_call_masking("9482431130", "7997931130"))
