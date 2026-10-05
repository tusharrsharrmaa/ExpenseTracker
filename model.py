from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime
from database import Base
from datetime import date, datetime, timezone
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    user_ID = Column(Integer, ForeignKey("users.id"), nullable=False)
    expense_date = Column(Date , default=date.today)
    
class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)