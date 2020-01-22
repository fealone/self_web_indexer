import binascii
import os
from pydantic import BaseModel
from typing import Any

from .redis import redis


tasks: dict = {}


class Task(BaseModel):
    task_id: str = binascii.hexlify(os.urandom(32)).decode()
    is_cancelled: bool = False
    user_id: int
    task_name: str
    task: Any
    args: list

    def __call__(self):
        task_key = f"{self.user_id}#{self.task_name}#{self.task_id}"
        tasks[task_key] = self
        redis.set(task_key, "inprogress")
        try:
            self.task(self, *self.args)
            if self.is_cancelled:
                redis.set(task_key, "cancelled")
                return
            redis.set(task_key, "completed")
        except Exception:
            redis.set(task_key, "failed")
        finally:
            del tasks[task_key]


def get_status(user_id: int, task_name: str, task_id: str):
    task_key = f"{user_id}#{task_name}#{task_id}"
    status = redis.get(task_key)
    return status


def cancel_task(user_id: int, task_name: str, task_id: str):
    task_key = f"{user_id}#{task_name}#{task_id}"
    if task_key in tasks:
        tasks[task_key].is_cancelled = True
        return True
    return False
