from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="FastAPI Data Entry Service",
    description="A API application for submitting and searching data entries.",
    version="1.0.0"
)

app.include_router(router)
