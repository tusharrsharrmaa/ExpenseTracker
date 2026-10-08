from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database import engine, Base
import model
from routers import auth, expenses, users
from exceptions import BusinessRuleError

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Expense Tracker API",
    description="Track expenses per user with JWT authentication.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)


@app.exception_handler(BusinessRuleError)
def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.get("/", tags=["Health"])
def root():
    return {"message": "Expense Tracker API is running"}