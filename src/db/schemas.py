from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

# class UserCreate(UserBase):
#     pass

# class User(UserBase):
#     id: int

#     class config:
#         # orm_mode = True
#         from_attributes = True
