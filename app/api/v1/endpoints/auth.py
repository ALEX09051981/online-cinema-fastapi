from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserRegistration, ActivationToken, UserResponse
from app.core.database import get_db
from app.crud.user import create_user, get_user_by_email, create_activation_token, get_activation_token
from app.services.email import send_activation_email
from app.tasks.user import remove_expired_tokens_task
from app.core.security import get_password_hash
from app.models.user import User

router = APIRouter()


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
