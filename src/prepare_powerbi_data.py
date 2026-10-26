"""Data preparation script for Power BI Dashboard.
Reads the raw pollution dataset, applies robust cleaning & feature engineering,
and exports a clean Star Schema data model with Dimension and Fact tables into `powerbi/data/`.
"""

import csv
import os
import math
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "Indian_cities_daily_pollution_2015-2020.csv")
POWERBI_DATA_DIR = os.path.join(BASE_DIR, "powerbi", "data")
os.makedirs(POWERBI_DATA_DIR, exist_ok=True)

# City metadata dictionary
CITY_META = {
    'Ahmedabad': {'state': 'Gujarat', 'region': 'Western', 'lat': 23.0225, 'lon': 72.5714, 'is_metro': 1},
    'Aizawl': {'state': 'Mizoram', 'region': 'North Eastern', 'lat': 23.7271, 'lon': 92.7176, 'is_metro': 0},
    'Amaravati': {'state': 'Andhra Pradesh', 'region': 'Southern', 'lat': 16.5417, 'lon': 80.5158, 'is_metro': 0},
    'Amritsar': {'state': 'Punjab', 'region': 'Northern', 'lat': 31.6340, 'lon': 74.8723, 'is_metro': 0},
    'Bengaluru': {'state': 'Karnataka', 'region': 'Southern', 'lat': 12.9716, 'lon': 77.5946, 'is_metro': 1},
    'Bhopal': {'state': 'Madhya Pradesh', 'region': 'Central', 'lat': 23.2599, 'lon': 77.4126, 'is_metro': 0},
    'Brajrajnagar': {'state': 'Odisha', 'region': 'Eastern', 'lat': 21.8247, 'lon': 83.9189, 'is_metro': 0},
    'Chandigarh': {'state': 'Chandigarh', 'region': 'Northern', 'lat': 30.7333, 'lon': 76.7794, 'is_metro': 0},
    'Chennai': {'state': 'Tamil Nadu', 'region': 'Southern', 'lat': 13.0827, 'lon': 80.2707, 'is_metro': 1},
    'Coimbatore': {'state': 'Tamil Nadu', 'region': 'Southern', 'lat': 11.0168, 'lon': 76.9558, 'is_metro': 0},
    'Delhi': {'state': 'Delhi', 'region': 'Northern', 'lat': 28.6139, 'lon': 77.2090, 'is_metro': 1},
    'Ernakulam': {'state': 'Kerala', 'region': 'Southern', 'lat': 9.9816, 'lon': 76.2999, 'is_metro': 0},
    'Gurugram': {'state': 'Haryana', 'region': 'Northern', 'lat': 28.4595, 'lon': 77.0266, 'is_metro': 0},
    'Guwahati': {'state': 'Assam', 'region': 'North Eastern', 'lat': 26.1445, 'lon': 91.7362, 'is_metro': 0},
    'Hyderabad': {'state': 'Telangana', 'region': 'Southern', 'lat': 17.3850, 'lon': 78.4867, 'is_metro': 1},
    'Jaipur': {'state': 'Rajasthan', 'region': 'Northern', 'lat': 26.9124, 'lon': 75.7873, 'is_metro': 0},
    'Jorapokhar': {'state': 'Jharkhand', 'region': 'Eastern', 'lat': 23.7042, 'lon': 86.4131, 'is_metro': 0},
    'Kochi': {'state': 'Kerala', 'region': 'Southern', 'lat': 9.9312, 'lon': 76.2673, 'is_metro': 0},
    'Kolkata': {'state': 'West Bengal', 'region': 'Eastern', 'lat': 22.5726, 'lon': 88.3639, 'is_metro': 1},
    'Lucknow': {'state': 'Uttar Pradesh', 'region': 'Northern', 'lat': 26.8467, 'lon': 80.9462, 'is_metro': 0},
    'Mumbai': {'state': 'Maharashtra', 'region': 'Western', 'lat': 19.0760, 'lon': 72.8777, 'is_metro': 1},
    'Patna': {'state': 'Bihar', 'region': 'Eastern', 'lat': 25.5941, 'lon': 85.1376, 'is_metro': 0},
    'Shillong': {'state': 'Meghalaya', 'region': 'North Eastern', 'lat': 25.5788, 'lon': 91.8933, 'is_metro': 0},
    'Talcher': {'state': 'Odisha', 'region': 'Eastern', 'lat': 20.9509, 'lon': 85.2165, 'is_metro': 0},
    'Thiruvananthapuram': {'state': 'Kerala', 'region': 'Southern', 'lat': 8.5241, 'lon': 76.9366, 'is_metro': 0},
    'Visakhapatnam': {'state': 'Andhra Pradesh', 'region': 'Southern', 'lat': 17.6868, 'lon': 83.2185, 'is_metro': 0}
}

POLLUTANT_COLS = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene']

def safe_float(v):
    if v is None:
        return None
    val_str = str(v).strip()
    if val_str == '' or val_str.lower() in ('nan', 'null', 'none'):
        return None
    try:
        val = float(val_str)
        return val if val >= 0 else None
    except (ValueError, TypeError):
        return None

def get_season(month):
    if month in (12, 1, 2):
        return "Winter"
    elif month in (3,):
        return "Spring"
    elif month in (4, 5):
        return "Summer"
    elif month in (6, 7, 8):
        return "Monsoon"
    else:
        return "Post-monsoon"

def get_aqi_category(aqi, raw_bucket):
    if raw_bucket and raw_bucket.strip() in ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']:
        return raw_bucket.strip()
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

def get_lockdown_phase(dt):
    if dt.year != 2020:
        return "Pre-2020 Baseline"
    if dt < datetime(2020, 3, 24):
        return "Pre-Lockdown (2020)"
    elif datetime(2020, 3, 24) <= dt <= datetime(2020, 5, 31):
        return "Lockdown (2020)"
    else:
        return "Post-Lockdown (2020)"

def median_val(lst):
    cleaned = sorted([x for x in lst if x is not None])
    if not cleaned:
        return None
    n = len(cleaned)
    mid = n // 2
    return cleaned[mid] if n % 2 == 1 else (cleaned[mid - 1] + cleaned[mid]) / 2.0

def process_data():
    print("Reading raw dataset...")
    with open(RAW_DATA_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    print(f"Total raw rows: {len(raw_rows)}")

    # Parse and clean rows
    cleaned_rows = []
    city_numeric_values = defaultdict(lambda: defaultdict(list))
    global_numeric_values = defaultdict(list)

    for r in raw_rows:
        city = r.get('City', '').strip()
        date_str = r.get('Date', '').strip()
        if not city or not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        item = {
            'City': city,
            'Date': date_str,
            'DateTime': dt,
            'AQI_Bucket_Raw': r.get('AQI_Bucket', '').strip()
        }

        # Safe float conversion
        for col in POLLUTANT_COLS + ['AQI']:
            val = safe_float(r.get(col))
            item[col] = val
            if val is not None:
                city_numeric_values[col][city].append(val)
                global_numeric_values[col].append(val)

        cleaned_rows.append(item)

    # Compute medians for imputation
    city_medians = {col: {} for col in POLLUTANT_COLS + ['AQI']}
    global_medians = {col: median_val(global_numeric_values[col]) for col in POLLUTANT_COLS + ['AQI']}

    for col in POLLUTANT_COLS + ['AQI']:
        for city, vals in city_numeric_values[col].items():
            city_medians[col][city] = median_val(vals)

    # Apply imputations where appropriate
    for r in cleaned_rows:
        city = r['City']
        for col in POLLUTANT_COLS + ['AQI']:
            if r[col] is None:
                med = city_medians[col].get(city)
                if med is None:
                    med = global_medians[col]
                r[col] = med

        # Recalculate AQI category
        r['AQI_Category'] = get_aqi_category(r['AQI'], r['AQI_Bucket_Raw'])

    # Sort by City and Date for rolling window computations
    cleaned_rows.sort(key=lambda x: (x['City'], x['Date']))

    # Rolling AQI windows
    city_groups = defaultdict(list)
    for r in cleaned_rows:
        city_groups[r['City']].append(r)

    for city, grp in city_groups.items():
        aqi_list = [r['AQI'] for r in grp]
        for i, r in enumerate(grp):
            # 7-day rolling window
            w7 = [v for v in aqi_list[max(0, i-6):i+1] if v is not None]
            r['Rolling_7Day_AQI'] = round(sum(w7) / len(w7), 2) if w7 else r['AQI']
            # 30-day rolling window
            w30 = [v for v in aqi_list[max(0, i-29):i+1] if v is not None]
            r['Rolling_30Day_AQI'] = round(sum(w30) / len(w30), 2) if w30 else r['AQI']

    # Compute Year-City Rank
    year_city_aqis = defaultdict(lambda: defaultdict(list))
    for r in cleaned_rows:
        yr = r['DateTime'].year
        year_city_aqis[yr][r['City']].append(r['AQI'])

    year_city_rank = {}
    for yr, cdict in year_city_aqis.items():
        avg_aqis = {c: sum(v)/len(v) for c, v in cdict.items()}
        sorted_ranks = sorted(avg_aqis.items(), key=lambda x: x[1], reverse=True)
        for rank, (c, _) in enumerate(sorted_ranks, 1):
            year_city_rank[(c, yr)] = rank

    # Dominant pollutant & Exceedances
    for r in cleaned_rows:
        # Dominant pollutant
        max_pol = 'PM2.5'
        max_val = -1.0
        for p in POLLUTANT_COLS:
            val = r[p]
            if val is not None and val > max_val:
                max_val = val
                max_pol = p
        r['Dominant_Pollutant'] = max_pol

        # Ratios
        pm25 = r.get('PM2.5') or 0
        pm10 = r.get('PM10') or 0
        r['PM25_PM10_Ratio'] = round(pm25 / pm10, 4) if pm10 > 0 else 0.0

        # NAAQS Exceed: PM2.5 > 60 or PM10 > 100
        r['NAAQS_Exceed'] = 1 if (pm25 > 60 or pm10 > 100) else 0
        # WHO Exceed: PM2.5 > 15
        r['WHO_Exceed'] = 1 if pm25 > 15 else 0

        # Lockdown period
        dt = r['DateTime']
        r['Lockdown_Flag'] = 1 if (dt.year == 2020 and datetime(2020, 3, 24) <= dt <= datetime(2020, 5, 31)) else 0
        r['Lockdown_Phase'] = get_lockdown_phase(dt)

        # City rank
        r['City_Year_Rank'] = year_city_rank.get((r['City'], dt.year), 1)

    print("Data enrichment complete. Generating Star Schema dimension & fact tables...")

    # 1. Dim_City
    cities_in_data = sorted(list(set(r['City'] for r in cleaned_rows)))
    dim_city_path = os.path.join(POWERBI_DATA_DIR, "Dim_City.csv")
    with open(dim_city_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['City_Key', 'City', 'State', 'Region', 'Latitude', 'Longitude', 'Is_Metropolitan'])
        for idx, city in enumerate(cities_in_data, 1):
            meta = CITY_META.get(city, {'state': 'India', 'region': 'Other', 'lat': 20.5937, 'lon': 78.9629, 'is_metro': 0})
            writer.writerow([idx, city, meta['state'], meta['region'], meta['lat'], meta['lon'], meta['is_metro']])
    print(f"✅ Generated {dim_city_path} ({len(cities_in_data)} cities)")

    # 2. Dim_Date
    dates_in_data = sorted(list(set(r['Date'] for r in cleaned_rows)))
    dim_date_path = os.path.join(POWERBI_DATA_DIR, "Dim_Date.csv")
    with open(dim_date_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Date', 'Year', 'Quarter', 'Quarter_Name', 'Month', 'Month_Name', 'Month_Short',
            'Year_Month', 'Day', 'Day_Of_Week', 'Day_Of_Week_Number', 'Is_Weekend',
            'Season', 'Lockdown_Phase', 'Is_Lockdown'
        ])
        for d_str in dates_in_data:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            q = (dt.month - 1) // 3 + 1
            is_weekend = 1 if dt.weekday() >= 5 else 0
            is_lockdown = 1 if (dt.year == 2020 and datetime(2020, 3, 24) <= dt <= datetime(2020, 5, 31)) else 0
            writer.writerow([
                d_str,
                dt.year,
                q,
                f"{dt.year} Q{q}",
                dt.month,
                dt.strftime('%B'),
                dt.strftime('%b'),
                dt.strftime('%Y-%m'),
                dt.day,
                dt.strftime('%A'),
                dt.isoweekday(),
                is_weekend,
                get_season(dt.month),
                get_lockdown_phase(dt),
                is_lockdown
            ])
    print(f"✅ Generated {dim_date_path} ({len(dates_in_data)} dates)")

    # 3. Dim_AQI_Category
    dim_cat_path = os.path.join(POWERBI_DATA_DIR, "Dim_AQI_Category.csv")
    categories = [
        (1, 'Good', 0, 50, '#00E400', 'Minimal health impact; clean and safe air.'),
        (2, 'Satisfactory', 51, 100, '#92D050', 'Minor breathing discomfort to sensitive people.'),
        (3, 'Moderate', 101, 200, '#FFFF00', 'Breathing discomfort to people with lungs, asthma, and heart diseases.'),
        (4, 'Poor', 201, 300, '#FF7E00', 'Breathing discomfort to most people on prolonged exposure.'),
        (5, 'Very Poor', 301, 400, '#FF0000', 'Respiratory illness on prolonged exposure.'),
        (6, 'Severe', 401, 1000, '#7E0023', 'Affects healthy people and seriously impacts those with existing diseases.')
    ]
    with open(dim_cat_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Category_Key', 'Category_Name', 'AQI_Min', 'AQI_Max', 'Color_Hex', 'Health_Impact'])
        for cat in categories:
            writer.writerow(cat)
    print(f"✅ Generated {dim_cat_path}")

    # 4. Dim_Pollutant
    dim_pol_path = os.path.join(POWERBI_DATA_DIR, "Dim_Pollutant.csv")
    pollutants = [
        ('PM2.5', 'Particulate Matter 2.5', 'µg/m³', 60, 15, 'Vehicle emissions, biomass burning, industrial combustion'),
        ('PM10', 'Particulate Matter 10', 'µg/m³', 100, 45, 'Road dust, construction, agricultural burning'),
        ('NO', 'Nitric Oxide', 'µg/m³', 0, 0, 'Combustion in motor vehicles and power plants'),
        ('NO2', 'Nitrogen Dioxide', 'µg/m³', 80, 25, 'High-temperature fuel burning, heavy diesel transport'),
        ('NOx', 'Total Nitrogen Oxides', 'µg/m³', 80, 30, 'Combined vehicular and industrial emissions'),
        ('NH3', 'Ammonia', 'µg/m³', 400, 0, 'Agricultural fertilizers, animal waste, sewage'),
        ('CO', 'Carbon Monoxide', 'mg/m³', 2.0, 4.0, 'Incomplete fossil fuel combustion, urban traffic'),
        ('SO2', 'Sulphur Dioxide', 'µg/m³', 80, 40, 'Thermal power plants, coal burning, oil refineries'),
        ('O3', 'Ground-Level Ozone', 'µg/m³', 100, 100, 'Photochemical reaction of NOx and VOCs in sunlight'),
        ('Benzene', 'Benzene', 'µg/m³', 5, 0, 'Petroleum storage, vehicle refueling, industrial solvent'),
        ('Toluene', 'Toluene', 'µg/m³', 0, 0, 'Paints, thinners, vehicle exhaust, industrial printing')
    ]
    with open(dim_pol_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pollutant_Code', 'Pollutant_Name', 'Unit', 'CPCB_Limit_24hr', 'WHO_Limit_24hr', 'Primary_Sources'])
        for pol in pollutants:
            writer.writerow(pol)
    print(f"✅ Generated {dim_pol_path}")

    # 5. Fact_Daily_Readings
    fact_readings_path = os.path.join(POWERBI_DATA_DIR, "Fact_Daily_Readings.csv")
    fact_headers = [
        'Reading_ID', 'Date', 'City', 'State', 'Region', 'PM2.5', 'PM10', 'NO', 'NO2', 'NOx',
        'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'AQI', 'AQI_Category', 'PM25_PM10_Ratio',
        'NAAQS_Exceed', 'WHO_Exceed', 'Rolling_7Day_AQI', 'Rolling_30Day_AQI', 'Lockdown_Flag',
        'Lockdown_Phase', 'Dominant_Pollutant', 'City_Year_Rank'
    ]
    with open(fact_readings_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fact_headers)
        for idx, r in enumerate(cleaned_rows, 1):
            city_meta = CITY_META.get(r['City'], {'state': 'India', 'region': 'Other'})
            writer.writerow([
                idx,
                r['Date'],
                r['City'],
                city_meta['state'],
                city_meta['region'],
                round(r['PM2.5'], 2) if r['PM2.5'] is not None else '',
                round(r['PM10'], 2) if r['PM10'] is not None else '',
                round(r['NO'], 2) if r['NO'] is not None else '',
                round(r['NO2'], 2) if r['NO2'] is not None else '',
                round(r['NOx'], 2) if r['NOx'] is not None else '',
                round(r['NH3'], 2) if r['NH3'] is not None else '',
                round(r['CO'], 2) if r['CO'] is not None else '',
                round(r['SO2'], 2) if r['SO2'] is not None else '',
                round(r['O3'], 2) if r['O3'] is not None else '',
                round(r['Benzene'], 2) if r['Benzene'] is not None else '',
                round(r['Toluene'], 2) if r['Toluene'] is not None else '',
                round(r['AQI'], 1) if r['AQI'] is not None else '',
                r['AQI_Category'],
                r['PM25_PM10_Ratio'],
                r['NAAQS_Exceed'],
                r['WHO_Exceed'],
                r['Rolling_7Day_AQI'],
                r['Rolling_30Day_AQI'],
                r['Lockdown_Flag'],
                r['Lockdown_Phase'],
                r['Dominant_Pollutant'],
                r['City_Year_Rank']
            ])
    print(f"✅ Generated {fact_readings_path} ({len(cleaned_rows)} records)")

    # 6. Fact_City_Monthly_Summary (Aggregated for Fast Executive Visuals)
    monthly_agg = defaultdict(lambda: {
        'count': 0, 'aqi_sum': 0.0, 'pm25_sum': 0.0, 'pm10_sum': 0.0,
        'severe_days': 0, 'very_poor_days': 0, 'good_days': 0,
        'naaqs_exceed_days': 0, 'who_exceed_days': 0
    })

    for r in cleaned_rows:
        yr_mo = r['DateTime'].strftime('%Y-%m')
        key = (r['City'], yr_mo)
        agg = monthly_agg[key]
        agg['count'] += 1
        agg['aqi_sum'] += r['AQI']
        agg['pm25_sum'] += (r['PM2.5'] or 0)
        agg['pm10_sum'] += (r['PM10'] or 0)
        if r['AQI_Category'] == 'Severe':
            agg['severe_days'] += 1
        elif r['AQI_Category'] == 'Very Poor':
            agg['very_poor_days'] += 1
        elif r['AQI_Category'] == 'Good':
            agg['good_days'] += 1
        if r['NAAQS_Exceed'] == 1:
            agg['naaqs_exceed_days'] += 1
        if r['WHO_Exceed'] == 1:
            agg['who_exceed_days'] += 1

    fact_monthly_path = os.path.join(POWERBI_DATA_DIR, "Fact_City_Monthly_Summary.csv")
    with open(fact_monthly_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'City', 'Year_Month', 'State', 'Region', 'Days_Monitored', 'Avg_AQI',
            'Avg_PM25', 'Avg_PM10', 'Severe_Days', 'Very_Poor_Days', 'Good_Days',
            'NAAQS_Exceed_Pct', 'WHO_Exceed_Pct'
        ])
        for (city, yr_mo), data in sorted(monthly_agg.items()):
            cnt = data['count']
            city_meta = CITY_META.get(city, {'state': 'India', 'region': 'Other'})
            writer.writerow([
                city,
                yr_mo,
                city_meta['state'],
                city_meta['region'],
                cnt,
                round(data['aqi_sum'] / cnt, 1),
                round(data['pm25_sum'] / cnt, 1),
                round(data['pm10_sum'] / cnt, 1),
                data['severe_days'],
                data['very_poor_days'],
                data['good_days'],
                round(data['naaqs_exceed_days'] / cnt * 100, 1),
                round(data['who_exceed_days'] / cnt * 100, 1)
            ])
    print(f"✅ Generated {fact_monthly_path} ({len(monthly_agg)} city-months)")

    # 7. Fact_Lockdown_Impact.csv
    # Comparing 2020 Pre-Lockdown (Jan 1 - Mar 23), Lockdown (Mar 24 - May 31), Post-Lockdown (Jun 1 - Jul 1)
    lockdown_stats = defaultdict(lambda: {
        'pre_sum': 0.0, 'pre_cnt': 0,
        'lock_sum': 0.0, 'lock_cnt': 0,
        'post_sum': 0.0, 'post_cnt': 0,
        'lock_pm25_sum': 0.0, 'pre_pm25_sum': 0.0,
        'lock_no2_sum': 0.0, 'pre_no2_sum': 0.0
    })

    for r in cleaned_rows:
        dt = r['DateTime']
        if dt.year == 2020:
            c = r['City']
            st = lockdown_stats[c]
            if dt < datetime(2020, 3, 24):
                st['pre_sum'] += r['AQI']
                st['pre_pm25_sum'] += (r['PM2.5'] or 0)
                st['pre_no2_sum'] += (r['NO2'] or 0)
                st['pre_cnt'] += 1
            elif datetime(2020, 3, 24) <= dt <= datetime(2020, 5, 31):
                st['lock_sum'] += r['AQI']
                st['lock_pm25_sum'] += (r['PM2.5'] or 0)
                st['lock_no2_sum'] += (r['NO2'] or 0)
                st['lock_cnt'] += 1
            else:
                st['post_sum'] += r['AQI']
                st['post_cnt'] += 1

    fact_lockdown_path = os.path.join(POWERBI_DATA_DIR, "Fact_Lockdown_Impact.csv")
    with open(fact_lockdown_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'City', 'State', 'Region', 'Pre_Lockdown_AQI', 'Lockdown_AQI', 'Post_Lockdown_AQI',
            'AQI_Drop_Points', 'Pct_AQI_Reduction', 'Pre_Lockdown_PM25', 'Lockdown_PM25',
            'Pct_PM25_Drop', 'Pre_Lockdown_NO2', 'Lockdown_NO2', 'Pct_NO2_Drop'
        ])
        for city, s in sorted(lockdown_stats.items()):
            pre_aqi = round(s['pre_sum'] / s['pre_cnt'], 1) if s['pre_cnt'] > 0 else 0
            lock_aqi = round(s['lock_sum'] / s['lock_cnt'], 1) if s['lock_cnt'] > 0 else 0
            post_aqi = round(s['post_sum'] / s['post_cnt'], 1) if s['post_cnt'] > 0 else 0
            aqi_drop = round(pre_aqi - lock_aqi, 1)
            pct_drop = round((aqi_drop / pre_aqi) * 100, 1) if pre_aqi > 0 else 0

            pre_pm = round(s['pre_pm25_sum'] / s['pre_cnt'], 1) if s['pre_cnt'] > 0 else 0
            lock_pm = round(s['lock_pm25_sum'] / s['lock_cnt'], 1) if s['lock_cnt'] > 0 else 0
            pct_pm_drop = round(((pre_pm - lock_pm) / pre_pm) * 100, 1) if pre_pm > 0 else 0

            pre_no2 = round(s['pre_no2_sum'] / s['pre_cnt'], 1) if s['pre_cnt'] > 0 else 0
            lock_no2 = round(s['lock_no2_sum'] / s['lock_cnt'], 1) if s['lock_cnt'] > 0 else 0
            pct_no2_drop = round(((pre_no2 - lock_no2) / pre_no2) * 100, 1) if pre_no2 > 0 else 0

            city_meta = CITY_META.get(city, {'state': 'India', 'region': 'Other'})
            writer.writerow([
                city, city_meta['state'], city_meta['region'], pre_aqi, lock_aqi, post_aqi,
                aqi_drop, pct_drop, pre_pm, lock_pm, pct_pm_drop, pre_no2, lock_no2, pct_no2_drop
            ])
    print(f"✅ Generated {fact_lockdown_path}")

    # Copy to data/processed as well so the main project stays aligned
    proc_feature_path = os.path.join(BASE_DIR, "data", "processed", "feature_data.csv")
    with open(proc_feature_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fact_headers)
        for idx, r in enumerate(cleaned_rows, 1):
            city_meta = CITY_META.get(r['City'], {'state': 'India', 'region': 'Other'})
            writer.writerow([
                idx, r['Date'], r['City'], city_meta['state'], city_meta['region'],
                r['PM2.5'], r['PM10'], r['NO'], r['NO2'], r['NOx'], r['NH3'], r['CO'],
                r['SO2'], r['O3'], r['Benzene'], r['Toluene'], r['AQI'], r['AQI_Category'],
                r['PM25_PM10_Ratio'], r['NAAQS_Exceed'], r['WHO_Exceed'], r['Rolling_7Day_AQI'],
                r['Rolling_30Day_AQI'], r['Lockdown_Flag'], r['Lockdown_Phase'],
                r['Dominant_Pollutant'], r['City_Year_Rank']
            ])
    print(f"✅ Updated {proc_feature_path} with valid AQI categories & full metadata.")

if __name__ == "__main__":
    process_data()
