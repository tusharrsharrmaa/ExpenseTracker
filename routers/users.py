from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from session import get_db
from model import User, UserSession
from schemas import UserCreate, UserUpdate, UserOut
from security import hash_password, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


# SIGNUP (public)
@router.post("", response_model=UserOut, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    db.refresh(new_user)
    return new_user


# MY PROFILE
@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# UPDATE MY PROFILE
@router.put("/me", response_model=UserOut)
def update_me(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user.email is not None:
        taken = (
            db.query(User)
            .filter(User.email == user.email, User.id != current_user.id)
            .first()
        )
        if taken:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user.email

    if user.name is not None:
        current_user.name = user.name

    if user.password is not None:
        current_user.password_hash = hash_password(user.password)
        # password changed -> log out everywhere
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id
        ).update({"is_revoked": True})

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already in use")

    db.refresh(current_user)
    return current_user


# DELETE MY ACCOUNT (expenses and sessions are deleted via the ORM cascade)
@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()