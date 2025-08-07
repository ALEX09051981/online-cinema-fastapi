from fastapi import FastAPI
from app.api.v1.endpoints import auth

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
