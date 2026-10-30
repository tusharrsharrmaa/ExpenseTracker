
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from session import get_db

from model import User, UserSession

from schemas import (
    UserCreate,
    UserUpdate,
    UserOut
)

from security import hash_password
from routers.auth import get_current_user


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================
# 1. SIGNUP
# POST /users
# PUBLIC ENDPOINT
# ==========================================

@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    try:

        # Check username
        existing_username = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
        )

        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

        # Check email
        existing_email = (
            db.query(User)
            .filter(User.email == user.email)
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        # Create new user
        new_user = User(
            name=user.name,
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password)
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error while creating user"
        )


# ==========================================
# 2. GET MY PROFILE
# GET /users/me
# PROTECTED ENDPOINT
# ==========================================

@router.get(
    "/me",
    response_model=UserOut
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user


# ==========================================
# 3. UPDATE MY PROFILE
# PUT /users/me
# PROTECTED ENDPOINT
# ==========================================

@router.put(
    "/me",
    response_model=UserOut
)
def update_me(

    user: UserUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    try:

        # Get only fields provided by user
        changes = user.model_dump(
            exclude_unset=True
        )

        # Prevent empty update
        if not changes:

            raise HTTPException(
                status_code=400,
                detail="Nothing to update"
            )

        # Reject explicit null values
        for field, value in changes.items():

            if value is None:

                raise HTTPException(
                    status_code=400,
                    detail=f"{field} cannot be empty"
                )

        # Update email
        if "email" in changes:

            existing_email = (
                db.query(User)
                .filter(
                    User.email == changes["email"],
                    User.id != current_user.id
                )
                .first()
            )

            if existing_email:

                raise HTTPException(
                    status_code=400,
                    detail="Email already in use"
                )

            current_user.email = changes["email"]

        # Update name
        if "name" in changes:

            current_user.name = changes["name"]

        # Update password
        if "password" in changes:

            current_user.password_hash = hash_password(
                changes["password"]
            )

            # Revoke all existing login sessions
            db.query(UserSession).filter(
                UserSession.user_id == current_user.id
            ).update(
                {"is_revoked": True},
                synchronize_session=False
            )

        # Save changes
        db.commit()

        db.refresh(current_user)

        return current_user

    except HTTPException:
        raise

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Email already in use"
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error while updating profile"
        )


# ==========================================
# 4. DELETE MY ACCOUNT
# DELETE /users/me
# PROTECTED ENDPOINT
# ==========================================

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_me(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    try:

        # Delete current user
        db.delete(current_user)

        # Commit deletion
        db.commit()

        return None

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error while deleting account"
        )
