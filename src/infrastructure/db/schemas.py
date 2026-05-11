from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    is_premium: bool

    class Config:
        from_attributes = True

class MemberOut(BaseModel):
    username: str
    status: str
    started_at: datetime
    expires_at: datetime | None = None

    class Config:
        from_attributes = True



# class UserCreate(UserBase):
#     pass

# class User(UserBase):
#     id: int

#     class config:
#         # orm_mode = True
#         from_attributes = True
