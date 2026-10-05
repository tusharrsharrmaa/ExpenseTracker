from datetime import date

from pydantic import BaseModel


# =========================
# EXPENSE SCHEMAS
# =========================

class ExpenseCreate(BaseModel):
    title: str | None = None
    amount: float
    category: str


class ExpenseUpdate(BaseModel):
    title: str | None = None
    amount: float | None = None
    category: str | None = None
    expense_date: date | None = None


class ExpenseOut(BaseModel):
    id: int
    title: str | None
    amount: float
    category: str
    user_ID: int
    expense_date: date

    class Config:
        from_attributes = True


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    
class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True