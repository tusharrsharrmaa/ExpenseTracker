from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from database import engine, Base
import model
from routers import expenses
from routers import users
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(expenses.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input data", "errors": exc.errors()}
    )


@app.get("/")
def root():
    return {
        "message": "Expense Tracker API is Running"
    }