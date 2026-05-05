import os
import httpx
from fastapi import HTTPException


async def verify_order(order_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api-m.paypal.com/v2/checkout/orders/{order_id}",
            auth=(os.getenv("PAYPAL_CLIENT_ID", ""), os.getenv("PAYPAL_SECRET", "")),
        )
    if res.status_code != 200 or res.json().get("status") != "COMPLETED":
        raise HTTPException(status_code=400, detail="PayPal order not completed")
    return True
