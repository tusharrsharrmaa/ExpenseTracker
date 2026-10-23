from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
import model
from routers.auth import get_current_user  

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: Optional[str] = None


class ExpenseOut(ExpenseCreate):
    id: int
    model_config = {"from_attributes": True}


def get_user_expense(db: Session, expense_id: int, user_id: int):
    expense = (
        db.query(model.Expense)
        .filter(model.Expense.id == expense_id, model.Expense.user_ID == user_id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = model.Expense(**data.model_dump(), user_ID=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense



@router.get("/", response_model=List[ExpenseOut])
def list_expenses(
    amount: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(model.Expense).filter(
        model.Expense.user_ID == current_user.id
    )

    if amount is not None:
        query = query.filter(model.Expense.amount == amount)

    return query.all()


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_expense(db, expense_id, current_user.id)


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user.id)
    for field, value in data.model_dump().items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user.id)
    db.delete(expense)
    db.commit()