from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from security import hash_password
from session import get_db
from model import User
from schemas import UserCreate, UserUpdate, UserOut





router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# CREATE USER
# =========================

@router.post("/", response_model=UserOut)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# GET ALL USERS
# =========================

@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users found"
        )

    return users


# =========================
# GET ONE USER
# =========================

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user



# =========================
# UPDATE USER
# =========================

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.email is not None:
        email_taken = (
            db.query(User)
            .filter(User.email == user.email, User.id != user_id)
            .first()
        )

        if email_taken:
            raise HTTPException(
                status_code=400,
                detail="Email already in use by another user"
            )

        existing_user.email = user.email

    if user.name is not None:
        existing_user.name = user.name

    if user.password is not None:
        existing_user.password_hash = hash_password(user.password)

    db.commit()
    db.refresh(existing_user)

    return existing_user


# =========================
# DELETE USER
# =========================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }