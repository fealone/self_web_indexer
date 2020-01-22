from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.lib.database import Base

from app.user import models

User = models.User


class PastFact(Base):
    __tablename__ = "past_facts"

    user_id = Column(Integer,
                     ForeignKey("users.id"),
                     primary_key=True,
                     index=True)
    url = Column(String(2048), primary_key=True, index=True)
    created_at = Column(DateTime, primary_key=True, index=True)
    fact = Column(String(1023))

    users = relationship("User", back_populates="past_facts")
