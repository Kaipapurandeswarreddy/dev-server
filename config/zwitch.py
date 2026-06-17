import httpx
import json
import os

from repos.user_types.driver import WalletDetails

KEY_ID = os.getenv("ZWITCH_KEY")
KEY_SECRET = os.getenv("ZWITCH_SECRET")
ACC_ID = os.getenv("ZWITCH_ACCOUNT_ID")

headers = {
    "Authorization": f"Bearer  {KEY_ID}:{KEY_SECRET}"
}

async def verify_bank_account(acc_details: WalletDetails, merchant_reference_id: str) -> str | None:
    url = f"https://api.zwitch.io/v1/verifications/bank-account"

    payload = {
        "force_penny_drop": False,
        "force_penny_drop_amount": 1,
        "bank_account_number": acc_details.account_no,
        "bank_ifsc_code": acc_details.ifsc_code,
        "merchant_reference_id": merchant_reference_id,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["status"]
    except httpx.HTTPError as e:
        print(f"Zwitch error: {e}")
        return None

async def create_zwitch_beneficiary(acc_details: WalletDetails, uid: str) -> str | None:
    url = f"https://api.zwitch.io/v1/accounts/{ACC_ID}/beneficiaries"

    payload = {
        "type": "account_number",
        "name_of_account_holder": acc_details.benf_name,
        "bank_account_number": acc_details.account_no,
        "bank_ifsc_code": acc_details.ifsc_code,
        "metadata": {
            "driver_uid": uid
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["id"]
    except httpx.HTTPError as e:
        print(f"Zwitch error: {e}")
        return None
    
async def update_zwitch_beneficiary_name(acc_details: WalletDetails):
    url = f"https://api.zwitch.io/v1/accounts/beneficiaries/{acc_details.benf_id}"

    payload = {
        "name_of_account_holder": acc_details.benf_name
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.HTTPError as e:
        print(f"Zwitch error: {e}")
        return None

async def delete_zwitch_beneficiary(beneficiary_id: str) -> bool:
    url = f"https://api.zwitch.io/v1/accounts/beneficiaries/{beneficiary_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["deleted"]
    except httpx.HTTPError as e:
        print(f"Zwitch error: {e}")
        return None

async def create_transfer(acc_details: WalletDetails, amount: float, merchant_reference_id: str):
    url = "https://api.zwitch.io/v1/transfers"

    payload = {
        "type": "account_number",
        "currency_code": "inr",
        "debit_account_id": ACC_ID,
        "beneficiary_id": acc_details.benf_id,
        "amount": amount,
        "currency_code": "inr",
        "payment_mode": "neft",
        "merchant_reference_id": merchant_reference_id,
        "async": False
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.HTTPError as e:
        print(f"Zwitch error: {e}")
        return None
