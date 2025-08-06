from sqlalchemy.orm import Session
from app.models.user import User, ActivationToken, UserGroup
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str):
    user_group = db.query(UserGroup).filter(UserGroup.name == "USER").first()
    if not user_group:
        user_group = UserGroup(name="USER")
        db.add(user_group)
        db.commit()
        db.refresh(user_group)

    db_user = User(
        email=email,
        hashed_password=hashed_password,
        group_id=user_group.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_activation_token(db: Session, user_id: int):
    token_value = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=24)
    db_token = ActivationToken(
        user_id=user_id,
        token=token_value,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_activation_token(db: Session, token: str):
    return db.query(ActivationToken).filter(ActivationToken.token == token).first()

def remove_expired_activation_tokens(db: Session):
    expired_tokens = db.query(ActivationToken).filter(ActivationToken.expires_at < datetime.utcnow()).all()
    for token in expired_tokens:
        db.delete(token)
    db.commit()
