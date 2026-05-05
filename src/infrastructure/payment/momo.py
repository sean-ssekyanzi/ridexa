import os
import uuid
import base64
import asyncio
import httpx
from fastapi import HTTPException

MOMO_SUBSCRIPTION_KEY = os.getenv("MOMO_SUBSCRIPTION_KEY", "")
MOMO_API_USER = os.getenv("MOMO_API_USER", "")
MOMO_API_KEY = os.getenv("MOMO_API_KEY", "")
MOMO_ENV = os.getenv("MOMO_ENVIRONMENT", "sandbox")
MOMO_BASE = "https://sandbox.momodeveloper.mtn.com" if MOMO_ENV == "sandbox" else "https://proxy.momoapi.mtn.com"


async def _get_token() -> str:
    credentials = base64.b64encode(f"{MOMO_API_USER}:{MOMO_API_KEY}".encode()).decode()
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{MOMO_BASE}/collection/token/",
            headers={"Authorization": f"Basic {credentials}",
                     "Ocp-Apim-Subscription-Key": MOMO_SUBSCRIPTION_KEY},
        )
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="MoMo auth failed")
    return res.json()["access_token"]


async def request_payment(phone: str) -> str:
    reference_id = str(uuid.uuid4())
    momo_token = await _get_token()

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{MOMO_BASE}/collection/v1_0/requesttopay",
            json={
                "amount": "4.99", "currency": "USD",
                "externalId": reference_id,
                "payer": {"partyIdType": "MSISDN", "partyId": phone},
                "payerMessage": "Ridexa Premium Subscription",
                "payeeNote": "Ridexa Premium",
            },
            headers={
                "Authorization": f"Bearer {momo_token}",
                "X-Reference-Id": reference_id,
                "X-Target-Environment": MOMO_ENV,
                "Ocp-Apim-Subscription-Key": MOMO_SUBSCRIPTION_KEY,
                "Content-Type": "application/json",
            },
        )
    if res.status_code not in (200, 202):
        raise HTTPException(status_code=400, detail="MoMo payment request failed")

    poll_headers = {
        "Authorization": f"Bearer {momo_token}",
        "X-Target-Environment": MOMO_ENV,
        "Ocp-Apim-Subscription-Key": MOMO_SUBSCRIPTION_KEY,
    }
    for _ in range(12):
        await asyncio.sleep(5)
        async with httpx.AsyncClient() as client:
            status_res = await client.get(
                f"{MOMO_BASE}/collection/v1_0/requesttopay/{reference_id}",
                headers=poll_headers,
            )
        if status_res.status_code == 200:
            result = status_res.json()
            if result.get("status") == "SUCCESSFUL":
                return reference_id
            if result.get("status") == "FAILED":
                raise HTTPException(status_code=400, detail="MoMo payment was declined")

    raise HTTPException(status_code=408, detail="MoMo payment timed out — please try again")
