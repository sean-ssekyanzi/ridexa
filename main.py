from fastapi import FastAPI, HTTPException, Depends, status, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db import models, schemas, services
from src.db.services import create_user, get_users, get_user_by_username, verify_token, authenticate_user, create_access_token
from src.db.connection import init_db, get_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from src.db.schemas import UserCreate
import os
from dotenv import load_dotenv
import stripe
import httpx
import uuid

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
MOMO_SUBSCRIPTION_KEY = os.getenv("MOMO_SUBSCRIPTION_KEY", "")
MOMO_API_USER = os.getenv("MOMO_API_USER", "")
MOMO_API_KEY = os.getenv("MOMO_API_KEY", "")
MOMO_ENV = os.getenv("MOMO_ENVIRONMENT", "sandbox")
MOMO_BASE = "https://sandbox.momodeveloper.mtn.com" if MOMO_ENV == "sandbox" else "https://proxy.momoapi.mtn.com"



#main app
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server is starting")
    await init_db()
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)

@app.get("/")
def main():
    return {"message": "Hello World"}



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: Annotated[str,Depends(oauth2_scheme)]):
    return {"token": token}





@app.get("/verify-token/{token}")
async def verify_user_token(token: str):
    await verify_token(token=token)
    return {"message":"Token is valid"}


@app.get("/me", response_model=schemas.UserOut)
async def get_me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = await verify_token(token=token)
    user = await get_user_by_username(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/create-checkout-session")
async def create_checkout_session(token: str = Depends(oauth2_scheme)):
    payload = await verify_token(token=token)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID"), "quantity": 1}],
        success_url=f"{FRONTEND_URL}/protected?premium=success",
        cancel_url=f"{FRONTEND_URL}/premium",
        metadata={"username": payload["sub"]},
    )
    return {"url": session.url}


@app.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        username = session_obj["metadata"]["username"]
        user = await get_user_by_username(db, username)
        if user:
            user.is_premium = True
            sub = models.Subscription(
                user_id=user.id,
                stripe_customer_id=session_obj.get("customer"),
                stripe_subscription_id=session_obj.get("subscription"),
                status="active",
                started_at=datetime.utcnow(),
            )
            db.add(sub)
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        stripe_sub_id = event["data"]["object"]["id"]
        from sqlalchemy import select
        result = await db.execute(select(models.Subscription).where(models.Subscription.stripe_subscription_id == stripe_sub_id))
        sub = result.scalars().first()
        if sub:
            sub.status = "cancelled"
            user = await db.get(models.User, sub.user_id)
            if user:
                user.is_premium = False
            await db.commit()

    return {"status": "ok"}


class PayPalConfirm(BaseModel):
    order_id: str

@app.post("/paypal-confirm")
async def paypal_confirm(body: PayPalConfirm, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = await verify_token(token=token)
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api-m.paypal.com/v2/checkout/orders/{body.order_id}",
            auth=(os.getenv("PAYPAL_CLIENT_ID", ""), os.getenv("PAYPAL_SECRET", "")),
        )
    if res.status_code != 200 or res.json().get("status") != "COMPLETED":
        raise HTTPException(status_code=400, detail="PayPal order not completed")
    user = await get_user_by_username(db, payload["sub"])
    if user and not user.is_premium:
        user.is_premium = True
        sub = models.Subscription(
            user_id=user.id,
            status="active",
            started_at=datetime.utcnow(),
        )
        db.add(sub)
        await db.commit()
    return {"status": "ok"}


class MomoRequest(BaseModel):
    phone: str

@app.post("/momo-pay")
async def momo_pay(body: MomoRequest, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = await verify_token(token=token)
    reference_id = str(uuid.uuid4())
    import base64, asyncio

    # Step 1: get MTN OAuth token
    credentials = base64.b64encode(f"{MOMO_API_USER}:{MOMO_API_KEY}".encode()).decode()
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            f"{MOMO_BASE}/collection/token/",
            headers={
                "Authorization": f"Basic {credentials}",
                "Ocp-Apim-Subscription-Key": MOMO_SUBSCRIPTION_KEY,
            },
        )
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="MoMo auth failed")
    momo_token = token_res.json()["access_token"]

    # Step 2: send payment prompt to phone
    req_headers = {
        "Authorization": f"Bearer {momo_token}",
        "X-Reference-Id": reference_id,
        "X-Target-Environment": MOMO_ENV,
        "Ocp-Apim-Subscription-Key": MOMO_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }
    momo_body = {
        "amount": "4.99",
        "currency": "USD",
        "externalId": reference_id,
        "payer": {"partyIdType": "MSISDN", "partyId": body.phone},
        "payerMessage": "Ridexa Premium Subscription",
        "payeeNote": "Ridexa Premium",
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{MOMO_BASE}/collection/v1_0/requesttopay", json=momo_body, headers=req_headers)
    if res.status_code not in (200, 202):
        raise HTTPException(status_code=400, detail="MoMo payment request failed")

    # Step 3: poll for payment confirmation (max 60s)
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
                user = await get_user_by_username(db, payload["sub"])
                if user and not user.is_premium:
                    user.is_premium = True
                    sub = models.Subscription(
                        user_id=user.id,
                        status="active",
                        started_at=datetime.utcnow(),
                    )
                    db.add(sub)
                    await db.commit()
                return {"status": "ok", "reference": reference_id}
            elif result.get("status") == "FAILED":
                raise HTTPException(status_code=400, detail="MoMo payment was declined")

    raise HTTPException(status_code=408, detail="MoMo payment timed out — please try again")
    


@app.post("/admin/activate-premium/{username}")
async def admin_activate_premium(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_premium = True
    from sqlalchemy import select
    result = await db.execute(select(models.Subscription).where(models.Subscription.user_id == user.id))
    sub = result.scalars().first()
    if not sub:
        sub = models.Subscription(user_id=user.id, status="active", started_at=datetime.utcnow())
        db.add(sub)
    else:
        sub.status = "active"
    await db.commit()
    return {"status": "ok", "username": username, "is_premium": True}


@app.get("/members", response_model=list[schemas.MemberOut])
async def get_members(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(models.User, models.Subscription)
        .join(models.Subscription, models.Subscription.user_id == models.User.id)
        .where(models.Subscription.status == "active")
    )
    return [
        schemas.MemberOut(
            username=user.username,
            status=sub.status,
            started_at=sub.started_at,
            expires_at=sub.expires_at,
        )
        for user, sub in result.all()
    ]


@app.get("/users/",response_model=list[UserCreate])
async def read_users(db: AsyncSession = Depends(get_db)):
    users = await get_users(db)
    return users

@app.post("/users/",response_model=UserCreate)
async def created_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user =  await create_user(db, user)
    return db_user

@app.post("/register")
async def register_user(user:UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(db=db, user=user)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


origins = [
    "https://ridexa-frntend.onrender.com",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:3000",

    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Port test 1")
port = int(os.environ.get("PORT",8000))

# class TransactionBase(BaseModel):
#     amount: float
#     category: str
#     description: str
#     is_income: bool
#     date: str

# class TransactionModel(TransactionBase):
#     id: int

#     class Config:
#         orm_mode = True

# def get_db():
#     db = lifespan()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated[Session, Depends(lifespan)]
# models.Base.metadata.create_all(bind=engine)

# @app.post("/transactions/",response_model=TransactionModel)
# async def create_transaction(transaction: TransactionBase, db:lifespan):