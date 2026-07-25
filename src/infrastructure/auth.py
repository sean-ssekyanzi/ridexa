from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.infrastructure.db.auth import SQLAuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    return await SQLAuthRepository.verify_token(token)
