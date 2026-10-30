
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from database import engine, Base
import model

from routers import auth, expenses, users

from exceptions import BusinessRuleError
from limiter import limiter


# ==========================================
# DATABASE TABLE CREATION
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Smart Expense Tracker API",
    description="Track expenses per user with JWT authentication.",
    version="1.0.0",
)


# ==========================================
# RATE LIMITING
# ==========================================

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://expensetracker-sydz.onrender.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REGISTER ROUTERS
# ==========================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)


# ==========================================
# BUSINESS RULE EXCEPTION HANDLER
# ==========================================

@app.exception_handler(BusinessRuleError)
async def business_rule_handler(
    request: Request,
    exc: BusinessRuleError
):

    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc)
        }
    )


# ==========================================
# VALIDATION ERROR HANDLER
# ==========================================

@app.exception_handler(RequestValidationError)
async def validation_handler(
    request: Request,
    exc: RequestValidationError
):

    return JSONResponse(
        status_code=422,
        content={
            "detail": jsonable_encoder(exc.errors())
        }
    )


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/", tags=["Health"])
def root():

    return {
        "message": "Expense Tracker API is running",
        "status": "success"
    }


# ==========================================
# FRONTEND STATIC FILES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.is_dir():

    app.mount(
        "/app",
        StaticFiles(
            directory=str(FRONTEND_DIR),
            html=True
        ),
        name="frontend"
    )
