# Feature engineering script for Indian air quality data (standard library)
"""
This script reads the cleaned CSV produced by `clean_data.py` (which uses only the
standard library), adds derived columns, and writes the enriched data to
`data/processed/feature_data.csv`.
All calculations are performed with the built‑in `csv` module and simple Python
logic – no external dependencies are required.
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLEANED_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "feature_data.csv")

# Helper functions ---------------------------------------------------
def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None

def month_name(m):
    return datetime(2000, m, 1).strftime('%B')

def season_from_month(m):
    if m in (12, 1, 2):
        return "Winter"
    if m in (3,):
        return "Spring"
    if m in (4, 5):
        return "Summer"
    if m in (6, 7, 8):
        return "Monsoon"
    return "Post-monsoon"

def safe_float(v):
    try:
        return float(v)
    except Exception:
        return None

# Main processing ----------------------------------------------------
with open(CLEANED_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Add time based features
for r in rows:
    dt = parse_date(r.get('Date'))
    if not dt:
        continue
    r['Year'] = dt.year
    r['Month'] = dt.month
    r['Month_Name'] = month_name(dt.month)
    r['Quarter'] = (dt.month - 1) // 3 + 1
    r['Day_Of_Week'] = dt.strftime('%A')
    r['Is_Weekend'] = int(r['Day_Of_Week'] in ('Saturday', 'Sunday'))
    r['Season'] = season_from_month(dt.month)

# AQI category (CPCB buckets 1‑6)
bucket_map = {"1": "Good", "2": "Satisfactory", "3": "Moderate", "4": "Poor", "5": "Very Poor", "6": "Severe"}
for r in rows:
    bucket = r.get('AQI_Bucket')
    r['AQI_Category'] = bucket_map.get(str(bucket), '')

# Pollutant ratios
for r in rows:
    pm25 = safe_float(r.get('PM2.5'))
    pm10 = safe_float(r.get('PM10'))
    r['PM25_PM10_Ratio'] = pm25 / pm10 if pm10 and pm10 > 0 else ''
    no = safe_float(r.get('NO'))
    no2 = safe_float(r.get('NO2'))
    nox = safe_float(r.get('NOx'))
    if no is not None and no2 is not None and nox is not None and (no + no2 + nox) > 0:
        r['Total_NOx_Ratio'] = (no + no2) / (no + no2 + nox)
    else:
        r['Total_NOx_Ratio'] = ''

# Exceedance flags
for r in rows:
    pm25 = safe_float(r.get('PM2.5'))
    pm10 = safe_float(r.get('PM10'))
    r['NAAQS_Exceed'] = int(pm25 is not None and pm25 > 60 and pm10 is not None and pm10 > 100)
    r['WHO_Exceed'] = int(pm25 is not None and pm25 > 15)

# Rolling averages – we compute per City using a simple sliding window
# First, sort rows by City then Date
rows.sort(key=lambda x: (x.get('City', ''), x.get('Date', '')))
city_groups = defaultdict(list)
for r in rows:
    city = r.get('City')
    city_groups[city].append(r)

for city, grp in city_groups.items():
    aqi_vals = [safe_float(r.get('AQI')) for r in grp]
    for i, r in enumerate(grp):
        # 7‑day rolling average
        window = aqi_vals[max(i-6, 0):i+1]
        window = [v for v in window if v is not None]
        r['Rolling_7Day_AQI'] = sum(window)/len(window) if window else ''
        # 30‑day rolling average
        window30 = aqi_vals[max(i-29, 0):i+1]
        window30 = [v for v in window30 if v is not None]
        r['Rolling_30Day_AQI'] = sum(window30)/len(window30) if window30 else ''

# Lockdown flag (Mar 24 – May 31 2020)
for r in rows:
    dt = parse_date(r.get('Date'))
    if dt and datetime(2020,3,24) <= dt <= datetime(2020,5,31):
        r['Lockdown_Flag'] = 1
    else:
        r['Lockdown_Flag'] = 0

# City rank by yearly average AQI
year_city_aqi = defaultdict(lambda: defaultdict(list))
for r in rows:
    city = r.get('City')
    year = r.get('Year')
    aqi = safe_float(r.get('AQI'))
    if city and year and aqi is not None:
        year_city_aqi[year][city].append(aqi)

city_year_rank = {}
for year, city_dict in year_city_aqi.items():
    avg_aqi = {c: sum(vals)/len(vals) for c, vals in city_dict.items()}
    sorted_c = sorted(avg_aqi.items(), key=lambda x: x[1], reverse=True)
    for rank, (c, _) in enumerate(sorted_c, start=1):
        city_year_rank[(c, year)] = rank

for r in rows:
    key = (r.get('City'), r.get('Year'))
    r['City_Rank'] = city_year_rank.get(key, '')

# Dominant pollutant (max concentration)
pollutant_cols = ['PM2.5','PM10','NO','NO2','NOx','NH3','CO','SO2','O3','Benzene','Toluene','Xylene']
for r in rows:
    max_col = ''
    max_val = -1
    for col in pollutant_cols:
        val = safe_float(r.get(col))
        if val is not None and val > max_val:
            max_val = val
            max_col = col
    r['Dominant_Pollutant'] = max_col

# Write output CSV (preserve column order – original plus new ones)
fieldnames = reader.fieldnames + [
    'Year','Month','Month_Name','Quarter','Day_Of_Week','Is_Weekend','Season',
    'AQI_Category','PM25_PM10_Ratio','Total_NOx_Ratio','NAAQS_Exceed','WHO_Exceed',
    'Rolling_7Day_AQI','Rolling_30Day_AQI','Lockdown_Flag','City_Rank','Dominant_Pollutant']

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as out_f:
    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Feature‑engineered data written to {OUTPUT_PATH}")
