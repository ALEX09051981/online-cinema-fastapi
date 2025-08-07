from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import RefreshToken
from app.schemas.user import UserRegistration, ActivationToken, UserResponse, UserLogin, TokenRevokeRequest
from app.core.database import get_db
from app.crud.user import create_user, get_user_by_email, create_activation_token, get_activation_token
from app.services.email import send_activation_email
from app.tasks.user import remove_expired_tokens_task
from app.core.security import get_password_hash
from app.core.security import verify_password, create_access_token, create_refresh_token
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_data.password)

    user = create_user(db, email=user_data.email, hashed_password=hashed_password)

    token = create_activation_token(db, user_id=user.id)

    await send_activation_email(user.email, token.token)

    remove_expired_tokens_task.delay()

    return user


@router.post("/activate")
def activate_account(token_data: ActivationToken, db: Session = Depends(get_db)):
    db_token = get_activation_token(db, token=token_data.token)

    if not db_token or db_token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token"
        )

    user = db_token.user
    user.is_active = True
    db.commit()
    db.delete(db_token)
    db.commit()

    return {"message": "Account activated successfully"}


@router.post("/login", response_model=Token)
def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_data.email)

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not activated. Please check your email for the activation link."
        )

    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: TokenRevokeRequest,
    db: Session = Depends(get_db)
):
    token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()

    if not token:
        return

    db.delete(token)
    db.commit()

    return
