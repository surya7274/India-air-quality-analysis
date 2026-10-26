"""Generate pre-aggregated dashboard JSON data for the interactive Power BI web simulator.
Provides instant rendering of all KPIs, charts, maps, and slicer interactions.
"""

import json
import csv
import os
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "powerbi", "data")
OUTPUT_JSON = os.path.join(BASE_DIR, "powerbi", "dashboard", "dashboard_data.json")

def generate():
    # Load Dim_City
    cities = {}
    with open(os.path.join(DATA_DIR, "Dim_City.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cities[r['City']] = {
                'city': r['City'],
                'state': r['State'],
                'region': r['Region'],
                'lat': float(r['Latitude']),
                'lon': float(r['Longitude']),
                'is_metro': int(r['Is_Metropolitan'])
            }

    # Load Dim_AQI_Category
    categories = []
    with open(os.path.join(DATA_DIR, "Dim_AQI_Category.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            categories.append({
                'name': r['Category_Name'],
                'min': int(r['AQI_Min']),
                'max': int(r['AQI_Max']),
                'color': r['Color_Hex'],
                'impact': r['Health_Impact']
            })

    # Load Fact_Lockdown_Impact
    lockdown = []
    with open(os.path.join(DATA_DIR, "Fact_Lockdown_Impact.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lockdown.append({
                'city': r['City'],
                'state': r['State'],
                'region': r['Region'],
                'pre_aqi': float(r['Pre_Lockdown_AQI']),
                'lock_aqi': float(r['Lockdown_AQI']),
                'post_aqi': float(r['Post_Lockdown_AQI']),
                'drop': float(r['AQI_Drop_Points']),
                'pct_drop': float(r['Pct_AQI_Reduction']),
                'pre_pm25': float(r['Pre_Lockdown_PM25']),
                'lock_pm25': float(r['Lockdown_PM25']),
                'pct_pm_drop': float(r['Pct_PM25_Drop']),
                'pre_no2': float(r['Pre_Lockdown_NO2']),
                'lock_no2': float(r['Lockdown_NO2']),
                'pct_no2_drop': float(r['Pct_NO2_Drop'])
            })

    # Load Fact_City_Monthly_Summary
    monthly = []
    with open(os.path.join(DATA_DIR, "Fact_City_Monthly_Summary.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            monthly.append({
                'city': r['City'],
                'ym': r['Year_Month'],
                'state': r['State'],
                'region': r['Region'],
                'days': int(r['Days_Monitored']),
                'avg_aqi': float(r['Avg_AQI']),
                'avg_pm25': float(r['Avg_PM25']),
                'avg_pm10': float(r['Avg_PM10']),
                'severe': int(r['Severe_Days']),
                'very_poor': int(r['Very_Poor_Days']),
                'good': int(r['Good_Days']),
                'naaqs_pct': float(r['NAAQS_Exceed_Pct']),
                'who_pct': float(r['WHO_Exceed_Pct'])
            })

    # Read Fact_Daily_Readings for high-level aggregations
    total_readings = 0
    aqi_sum = 0.0
    category_counts = defaultdict(int)
    yearly_city_aqi = defaultdict(lambda: defaultdict(list))
    season_aqi = defaultdict(list)
    dow_aqi = defaultdict(list)
    dominant_pollutants = defaultdict(int)
    city_readings_stats = defaultdict(lambda: {
        'count': 0, 'aqi_sum': 0.0, 'severe_count': 0, 'very_poor_count': 0,
        'naaqs_exceed': 0, 'who_exceed': 0, 'pm25_sum': 0.0, 'pm10_sum': 0.0,
        'no2_sum': 0.0, 'so2_sum': 0.0, 'co_sum': 0.0, 'o3_sum': 0.0
    })

    with open(os.path.join(DATA_DIR, "Fact_Daily_Readings.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            total_readings += 1
            aqi = float(r['AQI']) if r['AQI'] else 0.0
            aqi_sum += aqi
            cat = r['AQI_Category']
            category_counts[cat] += 1
            yr = int(r['Date'][:4])
            city = r['City']
            yearly_city_aqi[yr][city].append(aqi)

            # Day of week & Month
            month = int(r['Date'][5:7])
            # Season
            if month in (12, 1, 2):
                season = 'Winter'
            elif month == 3:
                season = 'Spring'
            elif month in (4, 5):
                season = 'Summer'
            elif month in (6, 7, 8):
                season = 'Monsoon'
            else:
                season = 'Post-monsoon'
            season_aqi[season].append(aqi)

            c_stats = city_readings_stats[city]
            c_stats['count'] += 1
            c_stats['aqi_sum'] += aqi
            if cat == 'Severe':
                c_stats['severe_count'] += 1
            elif cat == 'Very Poor':
                c_stats['very_poor_count'] += 1
            if r['NAAQS_Exceed'] == '1':
                c_stats['naaqs_exceed'] += 1
            if r['WHO_Exceed'] == '1':
                c_stats['who_exceed'] += 1

            for pol in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']:
                val = float(r[pol]) if r[pol] else 0.0
                c_stats[pol.lower().replace('.', '') + '_sum'] += val

            dominant_pollutants[r['Dominant_Pollutant']] += 1

    # City overall table
    city_summaries = []
    for city, s in city_readings_stats.items():
        cnt = s['count']
        meta = cities.get(city, {})
        city_summaries.append({
            'city': city,
            'state': meta.get('state', ''),
            'region': meta.get('region', ''),
            'lat': meta.get('lat', 0.0),
            'lon': meta.get('lon', 0.0),
            'is_metro': meta.get('is_metro', 0),
            'avg_aqi': round(s['aqi_sum'] / cnt, 1),
            'readings': cnt,
            'severe_days': s['severe_count'],
            'very_poor_days': s['very_poor_count'],
            'hazardous_pct': round((s['severe_count'] + s['very_poor_count']) / cnt * 100, 1),
            'naaqs_pct': round(s['naaqs_exceed'] / cnt * 100, 1),
            'who_pct': round(s['who_exceed'] / cnt * 100, 1),
            'avg_pm25': round(s['pm25_sum'] / cnt, 1),
            'avg_pm10': round(s['pm10_sum'] / cnt, 1),
            'avg_no2': round(s['no2_sum'] / cnt, 1),
            'avg_so2': round(s['so2_sum'] / cnt, 1),
            'avg_co': round(s['co_sum'] / cnt, 1),
            'avg_o3': round(s['o3_sum'] / cnt, 1),
            'fine_ratio': round(s['pm25_sum'] / s['pm10_sum'], 2) if s['pm10_sum'] > 0 else 0.0
        })

    # Sort cities by avg_aqi descending
    city_summaries.sort(key=lambda x: x['avg_aqi'], reverse=True)
    for idx, c in enumerate(city_summaries, 1):
        c['rank'] = idx

    # National Year Trend
    years_list = sorted(list(yearly_city_aqi.keys()))
    national_yearly = []
    for y in years_list:
        all_vals = []
        for c, v in yearly_city_aqi[y].items():
            all_vals.extend(v)
        national_yearly.append({
            'year': y,
            'avg_aqi': round(sum(all_vals) / len(all_vals), 1) if all_vals else 0
        })

    # Monthly national trend
    monthly_trend_dict = defaultdict(list)
    for m in monthly:
        monthly_trend_dict[m['ym']].append(m['avg_aqi'])
    monthly_series = [{'ym': ym, 'avg_aqi': round(sum(vals)/len(vals), 1)} for ym, vals in sorted(monthly_trend_dict.items())]

    # Stubble burning (Oct-Nov) across Northern cities vs other months
    stubble_delhi = []
    for m in monthly:
        if m['city'] in ['Delhi', 'Gurugram', 'Lucknow', 'Amritsar', 'Patna']:
            stubble_delhi.append(m)

    payload = {
        'meta': {
            'title': 'India Air Quality Analysis (2015 - 2020)',
            'total_readings': total_readings,
            'avg_aqi': round(aqi_sum / total_readings, 1),
            'total_cities': len(cities),
            'categories': categories,
            'years': years_list,
            'regions': sorted(list(set(c['region'] for c in cities.values())))
        },
        'city_summaries': city_summaries,
        'category_counts': dict(category_counts),
        'national_yearly': national_yearly,
        'monthly_series': monthly_series,
        'season_averages': {s: round(sum(v)/len(v), 1) for s, v in season_aqi.items()},
        'lockdown_impact': sorted(lockdown, key=lambda x: x['pct_drop'], reverse=True),
        'monthly_details': monthly,
        'dominant_pollutants': dict(dominant_pollutants)
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Generated dashboard JSON dataset: {OUTPUT_JSON} ({len(city_summaries)} cities, {len(monthly_series)} months)")

if __name__ == "__main__":
    generate()
