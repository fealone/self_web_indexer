from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.index.schemes import PastFact


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    past_facts: List[PastFact] = []

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    pass


class Token(TokenBase):
    token: str
    expired_at: datetime


class TokenCreate(TokenBase):
    user_id: int


class Authenticate(BaseModel):
    expire: int
    reuse: bool
