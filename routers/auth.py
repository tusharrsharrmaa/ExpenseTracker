
from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from session import get_db

from model import User, UserSession

from schemas import LoginRequest, Token

from security import (
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme,
    utcnow,
)


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# ==========================================
# UNAUTHORIZED ERROR
# ==========================================

def unauthorized(detail: str) -> HTTPException:

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


# ==========================================
# HELPER: CHECK TOKEN PAYLOAD
# ==========================================

def get_token_identity(payload: dict):

    if not isinstance(payload, dict):
        raise unauthorized("Invalid token")

    user_id = payload.get("sub")
    session_id = payload.get("sid")

    if not user_id or not session_id:
        raise unauthorized("Invalid token payload")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise unauthorized("Invalid token user ID")

    return user_id, session_id


# ==========================================
# HELPER: CHECK SESSION EXPIRATION
# ==========================================

def check_session_expiration(session: UserSession):

    now = utcnow()
    expires = session.expires_at

    if expires is None:
        raise unauthorized("Invalid session expiration")

    # MySQL may return a naive datetime.
    # Normalize current time for comparison.
    if expires.tzinfo is None:
        now = now.replace(tzinfo=None)

    if expires <= now:
        raise unauthorized("Session expired")


# ==========================================
# 1. LOGIN
# POST /auth/login
# ==========================================

@router.post(
    "/login",
    response_model=Token
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        # Find user by email
        user = (
            db.query(User)
            .filter(User.email == credentials.email)
            .first()
        )

        # Check user and password
        if not user or not verify_password(
            credentials.password,
            user.password_hash
        ):

            raise unauthorized("Invalid email or password")

        # Create database session
        new_session = UserSession(
            user_id=user.id,
            expires_at=utcnow() + timedelta(days=7)
        )

        db.add(new_session)

        db.commit()

        db.refresh(new_session)

        # Generate JWT token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "sid": new_session.id
            },
            expires_at=new_session.expires_at
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during login"
        )


# ==========================================
# 2. LOGOUT
# POST /auth/logout
# ==========================================

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        # Decode JWT token
        payload = decode_access_token(token)

        if payload is None:
            raise unauthorized("Invalid token")

        user_id, session_id = get_token_identity(payload)

        # Find session belonging to this user
        user_session = (
            db.query(UserSession)
            .filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
            .first()
        )

        if not user_session:
            raise unauthorized("Session not found")

        if user_session.is_revoked:
            raise unauthorized("Session already logged out")

        check_session_expiration(user_session)

        # Revoke session
        user_session.is_revoked = True

        db.commit()

        return {
            "message": "Logged out successfully"
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during logout"
        )


# ==========================================
# 3. GET CURRENT USER
# Used by protected routes
# ==========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        # Decode JWT token
        payload = decode_access_token(token)

        if payload is None:
            raise unauthorized("Invalid token")

        # Extract user ID and session ID
        user_id, session_id = get_token_identity(payload)

        # Find valid user session
        user_session = (
            db.query(UserSession)
            .filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
            .first()
        )

        if not user_session:
            raise unauthorized("Session not found")

        if user_session.is_revoked:
            raise unauthorized("Session expired or logged out")

        # Check expiration
        check_session_expiration(user_session)

        # Find user
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise unauthorized("User not found")

        return user

    except HTTPException:
        raise

    except SQLAlchemyError:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication"
        )
