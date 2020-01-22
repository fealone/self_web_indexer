import base64
import requests
from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks

from . import models, schemes
from app.lib.database import SessionLocal, engine
from app.lib.authorize import authorize
from app.lib import es
from app.lib import tasks
import elasticsearch

router = APIRouter()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def task_regist_index(self, url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    text = []
    for head in soup.find_all("p"):
        tx = head.find(text=True)
        if tx:
            text.append(tx)
    content = "\n".join(text)
    doc = {
        "url": url,
        "content": content
    }
    if self.is_cancelled:
        return
    _id = base64.b64encode(url.encode("utf-8")).decode("utf-8")
    es.es.index(index="web_index", doc_type="index", body=doc, id=_id)


@router.post("/index/_search", tags=["index"], status_code=200)
async def search_index(index: schemes.IndexSearch,
                       user: models.User = Depends(authorize)):
    doc = {
        "query": {
            "match": {
                "content": index.keywords
            }
        }
    }
    res = es.es.search(index="web_index", doc_type="index", body=doc)
    return {"results": res["hits"]["hits"]}


@router.post("/index/_regist", tags=["index"], status_code=202)
async def regist_index(index: schemes.IndexCreate,
                       bg_tasks: BackgroundTasks,
                       user: models.User = Depends(authorize)):
    task = tasks.Task(user_id=user.id,
                      task_name="regist_index",
                      task=task_regist_index,
                      args=[index.url])
    bg_tasks.add_task(task)
    return {"task_id": task.task_id}


@router.delete("/index/_delete", tags=["index"])
async def delete_index(index: schemes.IndexDelete,
                       user: models.User = Depends(authorize)):

    _id = base64.b64encode(index.url.encode("utf-8")).decode("utf-8")
    try:
        es.es.delete(index="web_index", doc_type="index", id=_id)
    except elasticsearch.exceptions.NotFoundError:
        raise HTTPException(status_code=404,
                            detail=f"It does not find the {index.url}.")

    return {}


@router.get("/index/task/{task_id}", tags=["index"])
async def get_regist_task(task_id: str,
                          user: models.User = Depends(authorize)):
    status = tasks.get_status(user_id=user.id,
                              task_name="regist_index",
                              task_id=task_id)
    if status:
        return {"task_id": task_id,
                "status": status}
    else:
        raise HTTPException(status_code=404,
                            detail="It does not find the task.")


@router.delete("/index/task/{task_id}", tags=["index"], status_code=202)
async def cancel_regist_task(task_id: str,
                             user: models.User = Depends(authorize)):
    is_cancelled = tasks.cancel_task(user_id=user.id,
                                     task_name="regist_index",
                                     task_id=task_id)
    if is_cancelled:
        return {"message": "Delete request has been received."}
    else:
        raise HTTPException(status_code=404,
                            detail="It does not find the inprogress task.")
