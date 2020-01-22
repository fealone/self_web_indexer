import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import (
        APIKeyHeader)

from app.user import crud
from app.lib.database import SessionLocal


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


api_key = APIKeyHeader(name="Authorization", auto_error=False)


async def authorize(authorization: str = Depends(api_key),
                    db: Session = Depends(get_db)):
    current_datetime = datetime.datetime.now()
    if authorization:
        auth = authorization.split(" ")
    else:
        raise HTTPException(
            status_code=401,
            detail="Could not validate token",
            headers={"WWW-Authenticate": ""},
        )
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate token",
        headers={"WWW-Authenticate": authorization},
    )
    if len(auth) != 2:
        raise credentials_exception
    if auth[0] != "Bearer":
        raise credentials_exception
    token = auth[1]
    token_user = crud.authorize_user(db, token)
    if not token_user:
        raise credentials_exception
    token, user = token_user
    del user.hashed_password
    if token.expired_at is None:
        return user
    if token.expired_at > current_datetime:
        return user
    else:
        raise credentials_exception
