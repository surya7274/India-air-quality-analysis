import csv
import os
from datetime import datetime

# Paths relative to project root
RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'Indian_cities_daily_pollution_2015-2020.csv')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
PROCESSED_PATH = os.path.join(PROCESSED_DIR, 'cleaned_data.csv')

# Ensure the processed directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def clean_row(row, all_columns):
    """Return a dict with cleaned values:
    * Empty strings become None
    * Numeric columns are cast to float when possible
    """
    cleaned = {}
    for col in all_columns:
        raw = row.get(col, '').strip()
        if raw == '' or raw.lower() == 'nan':
            cleaned[col] = None
        else:
            num = safe_float(raw)
            cleaned[col] = num if num is not None else raw
    return cleaned

def main():
    # Load raw CSV
    with open(RAW_DATA_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = [clean_row(r, columns) for r in reader]

    total_rows = len(rows)
    # Drop columns with >60% missing values
    missing_counts = {col: sum(1 for r in rows if r[col] is None) for col in columns}
    cols_to_drop = [col for col, cnt in missing_counts.items() if cnt / total_rows > 0.6]
    for col in cols_to_drop:
        for r in rows:
            r.pop(col, None)
    columns = [c for c in columns if c not in cols_to_drop]

    # Identify numeric columns (those where every non‑None value is a number)
    numeric_cols = []
    for col in columns:
        if all((r[col] is None or isinstance(r[col], (int, float))) for r in rows):
            numeric_cols.append(col)

    # Impute missing numeric values with city‑wise median (if City column exists)
    if 'City' in columns:
        # Build city -> list per column
        city_medians = {col: {} for col in numeric_cols}
        for col in numeric_cols:
            # gather values per city
            city_vals = {}
            for r in rows:
                city = r.get('City')
                val = r[col]
                if city is not None and val is not None:
                    city_vals.setdefault(city, []).append(val)
            # compute median per city
            for city, vals in city_vals.items():
                vals.sort()
                mid = len(vals) // 2
                median = vals[mid] if len(vals) % 2 == 1 else (vals[mid - 1] + vals[mid]) / 2
                city_medians[col][city] = median
        # fill missing values
        for r in rows:
            city = r.get('City')
            for col in numeric_cols:
                if r[col] is None:
                    r[col] = city_medians[col].get(city)
    else:
        # Global median fallback
        global_medians = {}
        for col in numeric_cols:
            vals = [r[col] for r in rows if r[col] is not None]
            vals.sort()
            if vals:
                mid = len(vals) // 2
                median = vals[mid] if len(vals) % 2 == 1 else (vals[mid - 1] + vals[mid]) / 2
                global_medians[col] = median
        for r in rows:
            for col in numeric_cols:
                if r[col] is None:
                    r[col] = global_medians.get(col)

    # Replace impossible negative values with median using the same logic as above
    for col in numeric_cols:
        for r in rows:
            if r[col] is not None and r[col] < 0:
                r[col] = None
    # Re‑impute after cleaning negatives (reuse city medians/global medians)
    # (logic duplicated for brevity)
    if 'City' in columns:
        for r in rows:
            city = r.get('City')
            for col in numeric_cols:
                if r[col] is None:
                    r[col] = city_medians[col].get(city)
    else:
        for r in rows:
            for col in numeric_cols:
                if r[col] is None:
                    r[col] = global_medians.get(col)

    # Ensure Date column is ISO formatted (YYYY‑MM‑DD) and drop rows where parsing fails
    cleaned_rows = []
    for r in rows:
        date_str = r.get('Date')
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            r['Date'] = dt.strftime('%Y-%m-%d')
            cleaned_rows.append(r)
        except Exception:
            # skip malformed dates
            continue

    # Write cleaned CSV
    with open(PROCESSED_PATH, 'w', newline='', encoding='utf-8') as out_f:
        writer = csv.DictWriter(out_f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"✅ Cleaned data saved to {PROCESSED_PATH} (rows: {len(cleaned_rows)})")

if __name__ == "__main__":
    main()
