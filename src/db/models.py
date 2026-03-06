from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Float, Boolean
from datetime import datetime
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    # email: Mapped[str] = mapped_column(unique=True,nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    # def __repr__(self):
    #     return f"<User(id={self.id}, username='{self.username}', email='{self.email}', password='{self.hashed_password}')>"
    

# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)
#     amount = Column(Float)
#     category = Column(String)
#     description = Column(String)
#     is_income = Column(Boolean)
#     date = Column(String)
    