from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field


def clean_category(v: str) -> str:
    v = v.strip().lower()
    if not v:
        raise ValueError("Category cannot be empty")
    if v.isdigit():
        raise ValueError("Category must be text, not a number")
    return v


def clean_email(v: str) -> str:
    return v.strip().lower()


Amount = Annotated[float, Field(gt=0, le=10_000_000, allow_inf_nan=False)]
Category = Annotated[str, Field(min_length=1, max_length=50), AfterValidator(clean_category)]
Email = Annotated[EmailStr, AfterValidator(clean_email)]
Password = Annotated[str, Field(min_length=8, max_length=72)]


# ===== EXPENSES =====

class ExpenseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(None, max_length=100)
    amount: Amount
    category: Category
    expense_date: date | None = None   # None -> today (model default)


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(None, max_length=100)
    amount: Amount | None = None
    category: Category | None = None
    expense_date: date | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    amount: float
    category: str
    user_ID: int
    expense_date: date


# ===== USERS =====

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: Email
    password: Password


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=100)
    email: Email | None = None
    password: Password | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


# ===== AUTH =====

class LoginRequest(BaseModel):
    email: Email
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str