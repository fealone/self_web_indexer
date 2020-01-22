from datetime import datetime
from pydantic import BaseModel


class IndexBase(BaseModel):
    url: str


class IndexCreate(IndexBase):
    pass


class IndexDelete(IndexBase):
    pass


class IndexSearch(BaseModel):
    keywords: str


class PastFactBase(BaseModel):
    url: str
    created_at: datetime
    fact: str


class PastFactCreate(PastFactBase):
    pass


class PastFact(PastFactBase):
    user_id: int

    class Config:
        orm_mode = True
