from fastapi import FastAPI
from app.backend.api import router

app = FastAPI()

app.include_router(router)
