from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import (
        HTTPBasic,
        HTTPBasicCredentials)

from . import crud, models, schemes
from app.lib.database import SessionLocal, engine
from app.lib.authorize import authorize

router = APIRouter()

security = HTTPBasic()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/user/_register", tags=["user"], response_model=schemes.User)
async def regist_user(user: schemes.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.post("/user/_authenticate", tags=["user"])
async def authenticate_user(
        authenticate: schemes.Authenticate,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security)):
    token = crud.authenticate_user(db,
                                   credentials.username,
                                   credentials.password,
                                   authenticate.expire,
                                   authenticate.reuse)
    if not token:
        raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basci"})
    return token


@router.post("/user/_authorize", tags=["user"])
async def authorize_user(user: models.User = Depends(authorize)):
    return user
