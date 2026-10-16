"""Compute key insights from the raw air quality CSV without external libraries.

The script reads the raw dataset (downloaded earlier) using the built‑in `csv` module,
handles missing values, and prints numbers that will be used in the README.
"""

import csv
from datetime import datetime
from collections import defaultdict

DATA_PATH = "/Users/suryajeetkashi/.gemini/antigravity/scratch/india-air-quality-analysis/data/raw/Indian_cities_daily_pollution_2015-2020.csv"

# Helper to safely convert to float
def to_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

city_aqi_sum = defaultdict(float)
city_aqi_cnt = defaultdict(int)
season_aqi_sum = defaultdict(float)
season_aqi_cnt = defaultdict(int)

lock_start = datetime(2020, 3, 24)
lock_end = datetime(2020, 5, 31)
pre_lock_aqi = []
lock_aqi = []
post_lock_aqi = []

season_map = {12:"Winter",1:"Winter",2:"Winter",3:"Spring",4:"Summer",5:"Summer",6:"Monsoon",7:"Monsoon",8:"Monsoon",9:"Post-monsoon",10:"Post-monsoon",11:"Post-monsoon"}

with open(DATA_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city = row.get('City')
        date_str = row.get('Date')
        aqi = to_float(row.get('AQI'))
        if not city or not date_str or aqi is None:
            continue
        # Parse date
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        # City AQI stats
        city_aqi_sum[city] += aqi
        city_aqi_cnt[city] += 1
        # Season AQI stats
        month = date.month
        season = season_map.get(month)
        if season:
            season_aqi_sum[season] += aqi
            season_aqi_cnt[season] += 1
        # Lockdown period
        if date.year == 2020:
            if lock_start <= date <= lock_end:
                lock_aqi.append(aqi)
            elif date < lock_start:
                pre_lock_aqi.append(aqi)
            else:
                post_lock_aqi.append(aqi)

# Compute most polluted city
most_city = max(city_aqi_sum, key=lambda c: city_aqi_sum[c]/city_aqi_cnt[c])
most_city_aqi = city_aqi_sum[most_city]/city_aqi_cnt[most_city]
# Compute worst season
worst_season = max(season_aqi_sum, key=lambda s: season_aqi_sum[s]/season_aqi_cnt[s])
worst_season_aqi = season_aqi_sum[worst_season]/season_aqi_cnt[worst_season]
# Lockdown averages
pre_avg = sum(pre_lock_aqi)/len(pre_lock_aqi) if pre_lock_aqi else None
lock_avg = sum(lock_aqi)/len(lock_aqi) if lock_aqi else None
post_avg = sum(post_lock_aqi)/len(post_lock_aqi) if post_lock_aqi else None

print(f"Most polluted city (by avg AQI): {most_city} ({most_city_aqi:.2f})")
print(f"Worst season (by avg AQI): {worst_season} ({worst_season_aqi:.2f})")
print(f"Pre‑lockdown avg AQI (2020): {pre_avg:.2f}" if pre_avg else "No pre‑lockdown data")
print(f"Lockdown avg AQI (2020): {lock_avg:.2f}" if lock_avg else "No lockdown data")
print(f"Post‑lockdown avg AQI (2020): {post_avg:.2f}" if post_avg else "No post‑lockdown data")
