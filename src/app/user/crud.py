import binascii
import datetime
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, schemes


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authorize_user(db: Session, token: str):
    db_user = db.query(models.Token, models.User).filter(
            models.Token.token == token).first()
    if db_user:
        return db_user
    return None


def authenticate_user(
        db: Session,
        email: str,
        password: str,
        expire: int,
        reuse: bool):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    current_datetime = datetime.datetime.now()
    expired_at = current_datetime + datetime.timedelta(seconds=expire)
    db_token = db.query(models.Token).filter(
            models.Token.user_id == user.id,
            models.Token.expired_at > expired_at).first()
    if db_token and expire != 0:
        return db_token.token
    db_token = db.query(models.Token).filter(
            models.Token.user_id == user.id).first()
    if reuse and db_token:
        token = db_token.token
    else:
        token = binascii.hexlify(os.urandom(32)).decode()
    if db_token:
        db_token.token = token
        if expire:
            db_token.expired_at = expired_at
        else:
            db_token.expired_at = None
    else:
        if expire:
            db_token = models.Token(user_id=user.id,
                                    token=token,
                                    expired_at=expired_at)
        else:
            db_token = models.Token(user_id=user.id,
                                    token=token,
                                    expired_at=None)
        db.add(db_token)
    db.commit()
    return token


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: schemes.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email,
                          name=user.name,
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_past_fact(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PastFact).offset(skip).limit(limit).all()
