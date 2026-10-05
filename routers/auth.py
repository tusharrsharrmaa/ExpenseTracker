from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from session import get_db
from model import User, UserSession
from schemas import LoginRequest, Token
from security import (
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == credentials.email)
        .first()
    )

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    new_session = UserSession(
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    access_token = create_access_token(
        data={"sub": user.email, "sid": new_session.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    session = (
        db.query(UserSession)
        .filter(UserSession.id == payload.get("sid"))
        .first()
    )

    if not session or session.is_revoked:
        raise HTTPException(status_code=401, detail="Session already logged out")

    session.is_revoked = True
    db.commit()

    return {"message": "Logged out successfully"}