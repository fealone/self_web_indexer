from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.lib.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, index=True)
    name = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(128))
    is_active = Column(Boolean, default=True)

    past_facts = relationship("PastFact", back_populates="users")


class Token(Base):
    __tablename__ = "tokens"
    user_id = Column(Integer,
                     ForeignKey("users.id"),
                     primary_key=True,
                     index=True)
    token = Column(String(128), primary_key=True, index=True)
    expired_at = Column(DateTime)
