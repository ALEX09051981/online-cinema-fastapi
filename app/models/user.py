from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group_id = Column(Integer, ForeignKey("user_groups.id"))
    group = relationship("UserGroup", back_populates="users")

    activation_token = relationship("ActivationToken", back_populates="user", uselist=False,
                                    cascade="all, delete-orphan")
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan")


class ActivationToken(Base):
    __tablename__ = "activation_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="activation_token")

    def is_expired(self):
        return datetime.utcnow() > self.expires_at


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="refresh_tokens")
