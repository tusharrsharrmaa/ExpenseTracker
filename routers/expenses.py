
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from session import get_db
import model

from schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseOut
)

from exceptions import BusinessRuleError
from routers.auth import get_current_user


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# ==========================================
# HELPER FUNCTION
# GET EXPENSE BELONGING TO CURRENT USER
# ==========================================

def get_user_expense(
    db: Session,
    expense_id: int,
    user_id: int
):

    expense = (
        db.query(model.Expense)
        .filter(
            model.Expense.id == expense_id,
            model.Expense.user_ID == user_id
        )
        .first()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    return expense


# ==========================================
# 1. CREATE EXPENSE
# POST /expenses/
# ==========================================

@router.post(
    "/",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    try:

        values = data.model_dump(exclude_unset=True)

        # Remove date if None
        if values.get("expense_date") is None:
            values.pop("expense_date", None)

        # User ID comes from JWT token
        values.pop("user_ID", None)

        expense = model.Expense(
            **values,
            user_ID=current_user.id
        )

        db.add(expense)

        db.commit()

        db.refresh(expense)

        return expense

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating expense"
        )


# ==========================================
# 2. LIST AND FILTER EXPENSES
# GET /expenses/
# ==========================================

@router.get(
    "/",
    response_model=List[ExpenseOut]
)
def list_expenses(

    amount: Optional[float] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    category: Optional[str] = None,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)

):

    # Validate amount
    if amount is not None and amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero"
        )

    if min_amount is not None and min_amount < 0:

        raise HTTPException(
            status_code=400,
            detail="Minimum amount cannot be negative"
        )

    if max_amount is not None and max_amount < 0:

        raise HTTPException(
            status_code=400,
            detail="Maximum amount cannot be negative"
        )

    if (
        min_amount is not None
        and max_amount is not None
        and min_amount > max_amount
    ):

        raise HTTPException(
            status_code=400,
            detail="min_amount cannot be greater than max_amount"
        )

    try:

        # Get only current user's expenses
        query = db.query(model.Expense).filter(
            model.Expense.user_ID == current_user.id
        )

        # Exact amount filter
        if amount is not None:

            query = query.filter(
                model.Expense.amount == amount
            )

        # Minimum amount filter
        if min_amount is not None:

            query = query.filter(
                model.Expense.amount >= min_amount
            )

        # Maximum amount filter
        if max_amount is not None:

            query = query.filter(
                model.Expense.amount <= max_amount
            )

        # Category search (case-insensitive)
        if category is not None:

            category = category.strip()

            if not category:
                raise HTTPException(
                    status_code=400,
                    detail="Category cannot be empty"
                )

            query = query.filter(
                model.Expense.category.ilike(
                    f"%{category}%"
                )
            )

        # Latest expenses first
        expenses = query.order_by(
            model.Expense.expense_date.desc(),
            model.Expense.id.desc()
        ).all()

        return expenses

    except SQLAlchemyError:

        raise HTTPException(
            status_code=500,
            detail="Database error while fetching expenses"
        )


# ==========================================
# 3. GET SINGLE EXPENSE
# GET /expenses/{expense_id}
# ==========================================

@router.get(
    "/{expense_id}",
    response_model=ExpenseOut
)
def get_expense(

    expense_id: int,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)

):

    try:

        expense = get_user_expense(
            db,
            expense_id,
            current_user.id
        )

        return expense

    except HTTPException:
        raise

    except SQLAlchemyError:

        raise HTTPException(
            status_code=500,
            detail="Database error while fetching expense"
        )


# ==========================================
# 4. UPDATE EXPENSE
# PUT /expenses/{expense_id}
# ==========================================

@router.put(
    "/{expense_id}",
    response_model=ExpenseOut
)
def update_expense(

    expense_id: int,
    data: ExpenseUpdate,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)

):

    try:

        # Find user's expense
        expense = get_user_expense(
            db,
            expense_id,
            current_user.id
        )

        # Get only provided fields
        changes = data.model_dump(
            exclude_unset=True
        )

        # Prevent changing ownership
        changes.pop("user_ID", None)

        # Check empty update
        if not changes:

            raise BusinessRuleError(
                "Nothing to update"
            )

        # Validate fields
        for field in (
            "amount",
            "category",
            "expense_date"
        ):

            if field in changes and changes[field] is None:

                raise BusinessRuleError(
                    f"{field} cannot be empty"
                )

        # Validate amount
        if "amount" in changes and changes["amount"] <= 0:

            raise BusinessRuleError(
                "Amount must be greater than zero"
            )

        # Validate category
        if "category" in changes and not changes["category"].strip():

            raise BusinessRuleError(
                "Category cannot be empty"
            )

        # Update fields dynamically
        for field, value in changes.items():

            setattr(expense, field, value)

        db.commit()

        db.refresh(expense)

        return expense

    except HTTPException:
        raise

    except BusinessRuleError as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error while updating expense"
        )


# ==========================================
# 5. DELETE EXPENSE
# DELETE /expenses/{expense_id}
# ==========================================

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense(

    expense_id: int,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)

):

    try:

        # Find user's expense
        expense = get_user_expense(
            db,
            expense_id,
            current_user.id
        )

        db.delete(expense)

        db.commit()

        return None

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error while deleting expense"
        )
