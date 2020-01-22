import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from . import models, schemes
from app.lib import es


def create_user_past_fact(db: Session,
                          item: schemes.PastFactCreate,
                          user_id: int):
    db_past_fact = models.PastFact(**item.dict(), user_id=user_id)
    db.add(db_past_fact)
    db.commit()
    db.refresh(db_past_fact)
    return db_past_fact
