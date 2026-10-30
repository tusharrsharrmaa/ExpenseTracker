from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from session import get_db                                    
import model
from exceptions import BusinessRuleError                      
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut 
from routers.auth import get_current_user                     

router = APIRouter(prefix="/expenses", tags=["Expenses"])

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
    values = data.model_dump()
    if values["expense_date"] is None:        
        values.pop("expense_date")
    expense = model.Expense(**values, user_ID=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=List[ExpenseOut])
def list_expenses(
    amount: Optional[float] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(model.Expense).filter(
        model.Expense.user_ID == current_user.id
    )

    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            raise HTTPException(
                status_code=400,
                detail="min_amount cannot be greater than max_amount",
            )

    if amount is not None:
        query = query.filter(model.Expense.amount == amount)
    if min_amount is not None:
        query = query.filter(model.Expense.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(model.Expense.amount <= max_amount)
    if category is not None:
        query = query.filter(model.Expense.category.ilike(category))

    
    return query.order_by(model.Expense.expense_date.desc(), model.Expense.id.desc()).all()


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
    data: ExpenseUpdate,                      
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user.id)

    changes = data.model_dump(exclude_unset=True)  
    if not changes:
        raise BusinessRuleError("Nothing to update")
    for field in ("amount", "category", "expense_date"):
        if field in changes and changes[field] is None:
            raise BusinessRuleError(f"{field} cannot be empty")

    for field, value in changes.items():
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