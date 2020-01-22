from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .user import view as user
from .index import view as index


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(user.router)
app.include_router(index.router)
