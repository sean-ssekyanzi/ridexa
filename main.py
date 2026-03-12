from fastapi import FastAPI, HTTPException, Depends,status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db import models, schemas, services
from src.db.services import create_user, get_users,get_user_by_username,verify_token,authenticate_user,create_access_token
from src.db.connection import init_db,get_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from src.db.schemas import UserCreate
import os
from dotenv import load_dotenv



#main app
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server is starting")
    await init_db()
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: Annotated[str,Depends(oauth2_scheme)]):
    return {"token": token}





@app.get("/verify-token/{token}")
async def verify_user_token(token: str):
    await verify_token(token=token)
    return {"message":"Token is valid"}
    

@app.get("/")
def main():
    return {"message": "Hello World"}

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