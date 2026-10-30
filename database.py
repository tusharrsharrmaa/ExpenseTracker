
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Check your .env file."
    )


# ==========================================
# SSL CERTIFICATE
# ==========================================

CA_PATH = os.path.join(BASE_DIR, "ca.pem")

if not os.path.isfile(CA_PATH):
    raise RuntimeError(
        f"SSL certificate not found: {CA_PATH}"
    )


# ==========================================
# DATABASE ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,
    connect_args={
        "ssl": {
            "ca": CA_PATH
        }
    }
)


# ==========================================
# SESSION FACTORY
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# BASE CLASS
# ==========================================

Base = declarative_base()
