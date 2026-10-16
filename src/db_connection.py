# db_connection.py
"""
Utility to create a SQLAlchemy engine using credentials from a .env file.
The .env file (ignored by git) should contain:
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=air_quality
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "air_quality")

if not all([DB_USER, DB_PASSWORD]):
    raise RuntimeError("Database credentials not found in .env. Please create a .env file.")

CONN_STR = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(CONN_STR, echo=False)

def get_engine():
    """Return a SQLAlchemy engine instance."""
    return engine

if __name__ == "__main__":
    # Simple test connection
    with engine.connect() as conn:
        result = conn.execute("SELECT version();")
        print("Connected to:", result.fetchone())
