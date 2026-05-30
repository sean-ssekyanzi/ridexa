from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.infrastructure.db.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    return await verify_token(token)
