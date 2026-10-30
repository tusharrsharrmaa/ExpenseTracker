
import os

from datetime import datetime, timezone

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from session import get_db
from model import User, UserSession


# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Check your .env file."
    )


# ==========================================
# JWT CONFIGURATION
# ==========================================

ALGORITHM = "HS256"


# ==========================================
# PASSWORD HASHING
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:

    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Password cannot exceed 72 bytes"
        )

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    if len(plain_password.encode("utf-8")) > 72:
        return False

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================================
# UTC TIME
# ==========================================

def utcnow() -> datetime:
    """
    Return naive UTC datetime.
    Compatible with MySQL DATETIME.
    """

    return datetime.now(timezone.utc).replace(
        tzinfo=None
    )


# ==========================================
# CREATE JWT ACCESS TOKEN
# ==========================================

def create_access_token(
    data: dict,
    expires_at: datetime
):

    to_encode = data.copy()

    to_encode["exp"] = expires_at

    encoded_token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_token


# ==========================================
# DECODE JWT ACCESS TOKEN
# ==========================================

def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None


# ==========================================
# OAUTH2 BEARER TOKEN
# ==========================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ==========================================
# UNAUTHORIZED EXCEPTION
# ==========================================

def unauthorized():

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


# ==========================================
# GET CURRENT USER
# PROTECTED ROUTE DEPENDENCY
# ==========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        # Step 1: Decode JWT
        payload = decode_access_token(token)

        if payload is None:
            raise unauthorized()

        # Step 2: Extract user and session IDs
        user_id = payload.get("sub")
        session_id = payload.get("sid")

        if not user_id or not session_id:
            raise unauthorized()

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise unauthorized()

        # Step 3: Find user's session
        user_session = (
            db.query(UserSession)
            .filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
            .first()
        )

        if user_session is None:
            raise unauthorized()

        # Step 4: Check revocation
        if user_session.is_revoked:
            raise unauthorized()

        # Step 5: Check session expiration
        if user_session.expires_at is None:
            raise unauthorized()

        if user_session.expires_at <= utcnow():
            raise unauthorized()

        # Step 6: Find user
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            raise unauthorized()

        # Step 7: Return authenticated user
        return user

    except HTTPException:
        raise

    except SQLAlchemyError:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication"
        )
