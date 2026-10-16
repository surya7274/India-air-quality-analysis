# load_to_postgres.py
"""Load the cleaned and feature‑engineered CSVs into PostgreSQL.
The script uses the SQLAlchemy engine defined in `db_connection.py`.
It assumes the PostgreSQL database and tables (from `schema.sql`) already exist.
"""

import csv
import os
from pathlib import Path
from sqlalchemy import Table, MetaData, insert
from db_connection import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEANED_CSV = PROCESSED_DIR / "cleaned_data.csv"
FEATURE_CSV = PROCESSED_DIR / "feature_data.csv"

engine = get_engine()
metadata = MetaData()
metadata.reflect(bind=engine)

# Helper to bulk insert from CSV using SQLAlchemy core
def load_csv_to_table(csv_path, table_name):
    table = Table(table_name, metadata, autoload_with=engine)
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert empty strings to None for DB nullability
            rows.append({k: (v if v != '' else None) for k, v in row.items()})
    # Insert in chunks to avoid huge transactions
    chunk_size = 5000
    with engine.begin() as conn:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i+chunk_size]
            conn.execute(insert(table), chunk)
    print(f"Inserted {len(rows)} rows into {table_name} from {csv_path.name}")

if __name__ == "__main__":
    # Load cleaned city‑level data – we'll use the `daily_readings` table for both CSVs
    load_csv_to_table(CLEANED_CSV, "daily_readings")
    # Load feature‑engineered data – overwrite same table for simplicity
    load_csv_to_table(FEATURE_CSV, "daily_readings")
    print("✅ Data loading complete.")
