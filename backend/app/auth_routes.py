from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = request.email.strip().lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        password_hash=hash_password(
            request.password
        ),
    )

    db.add(user)

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    email = request.email.strip().lower()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_authenticated_user(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user