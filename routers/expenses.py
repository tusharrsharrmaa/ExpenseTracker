from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from session import get_db
from model import Expense, User
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut
from security import get_current_user


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# =========================
# CREATE EXPENSE
# =========================

@router.post("/", response_model=ExpenseOut)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        #expense_date=expense.expense_date,
        user_ID=current_user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


# =========================
# GET ALL EXPENSES (with filters)
# =========================

@router.get("/", response_model=list[ExpenseOut])
def get_expenses(
    category: str = None,
    min_amount: float = None,
    max_amount: float = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Expense).filter(Expense.user_ID == current_user.id)

    if category and category.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Category must be text, not a number"
        )

    if category:
        query = query.filter(Expense.category == category)

    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)

    if start_date:
        query = query.filter(Expense.expense_date >= start_date)

    if end_date:
        query = query.filter(Expense.expense_date <= end_date)

    expenses = query.all()

    if not expenses:
        raise HTTPException(
            status_code=404,
            detail="No expenses found matching the given filters"
        )

    return expenses


# =========================
# MONTHLY SUMMARY (must be above /{expense_id})
# =========================

@router.get("/summary")
def get_summary(
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        Expense.category,
        func.sum(Expense.amount).label("total")
    ).filter(Expense.user_ID == current_user.id)

    if month:
        query = query.filter(func.month(Expense.expense_date) == month)

    if year:
        query = query.filter(func.year(Expense.expense_date) == year)

    results = query.group_by(Expense.category).all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No expenses found for the given period"
        )

    summary = {category: total for category, total in results}

    return summary


# =========================
# GET ONE EXPENSE
# =========================

@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    if expense.user_ID != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this expense"
        )

    return expense


# =========================
# UPDATE EXPENSE
# =========================

@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not existing_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    if existing_expense.user_ID != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to modify this expense"
        )

    if expense.title is not None:
        existing_expense.title = expense.title

    if expense.amount is not None:
        existing_expense.amount = expense.amount

    if expense.category is not None:
        existing_expense.category = expense.category

    if expense.expense_date is not None:
        existing_expense.expense_date = expense.expense_date

    db.commit()
    db.refresh(existing_expense)

    return existing_expense


# =========================
# DELETE EXPENSE
# =========================

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    if expense.user_ID != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this expense"
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }