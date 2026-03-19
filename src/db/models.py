from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    subscription: Mapped["Subscription"] = relationship(back_populates="user", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    stripe_customer_id: Mapped[str] = mapped_column(String, nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")  # active | cancelled
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscription")

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
    