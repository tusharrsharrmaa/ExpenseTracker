
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    ForeignKey,
    Boolean,
    DateTime
)

from sqlalchemy.orm import relationship

from database import Base


# ==========================================
# USER MODEL
# ==========================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    username = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(500),
        nullable=False
    )

    # One user can have multiple expenses
    expenses = relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user can have multiple sessions
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ==========================================
# EXPENSE MODEL
# ==========================================

class Expense(Base):

    __tablename__ = "expenses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(100),
        nullable=True
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    category = Column(
        String(50),
        nullable=False
    )

    user_ID = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    expense_date = Column(
        Date,
        nullable=False,
        default=date.today
    )

    # Each expense belongs to one user
    user = relationship(
        "User",
        back_populates="expenses"
    )


# ==========================================
# USER SESSION MODEL
# ==========================================

class UserSession(Base):

    __tablename__ = "sessions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # Each session belongs to one user
    user = relationship(
        "User",
        back_populates="sessions"
    )
