-- Business / Policy Queries for Air Quality Analysis

-- 1. Most polluted city by average AQI
/* Find the city with the highest average AQI across the entire dataset */
SELECT city, AVG(aqi) AS avg_aqi
FROM daily_readings
GROUP BY city
ORDER BY avg_aqi DESC
LIMIT 1;
-- Insight: This city consistently experiences the worst air quality.

-- 2. Least polluted city by average AQI
SELECT city, AVG(aqi) AS avg_aqi
FROM daily_readings
GROUP BY city
ORDER BY avg_aqi ASC
LIMIT 1;
-- Insight: This city enjoys relatively cleaner air.

-- 3. Yearly AQI trend per city (is air improving or worsening?)
/* Compute year‑over‑year change using LAG */
WITH yearly AS (
    SELECT city,
           EXTRACT(YEAR FROM date) AS yr,
           AVG(aqi) AS avg_aqi
    FROM daily_readings
    GROUP BY city, yr
)
SELECT city,
       yr,
       avg_aqi,
       LAG(avg_aqi) OVER (PARTITION BY city ORDER BY yr) AS prev_year_aqi,
       CASE WHEN LAG(avg_aqi) OVER (PARTITION BY city ORDER BY yr) IS NULL THEN NULL
            WHEN avg_aqi < LAG(avg_aqi) OVER (PARTITION BY city ORDER BY yr) THEN 'Improving'
            WHEN avg_aqi > LAG(avg_aqi) OVER (PARTITION BY city ORDER BY yr) THEN 'Worsening'
            ELSE 'No Change'
       END AS trend
FROM yearly
ORDER BY city, yr;
-- Insight: Shows whether each city’s air quality is getting better or worse over time.

-- 4. Monthly and seasonal pollution pattern (winter vs monsoon)
SELECT city,
       TO_CHAR(date, 'Month') AS month,
       CASE WHEN EXTRACT(MONTH FROM date) IN (12,1,2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM date) IN (3,4,5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM date) IN (6,7,8) THEN 'Monsoon'
            ELSE 'Post‑monsoon'
       END AS season,
       AVG(aqi) AS avg_aqi
FROM daily_readings
GROUP BY city, month, season
ORDER BY city, season, month;
-- Insight: Highlights peak pollution months and the impact of seasonal weather.

-- 5. Number of Severe / Very Poor days per city (AQI_BUCKET = 'Severe' OR 'Very Poor')
SELECT city,
       SUM(CASE WHEN aqi_bucket = 'Severe' THEN 1 ELSE 0 END) AS severe_days,
       SUM(CASE WHEN aqi_bucket = 'Very Poor' THEN 1 ELSE 0 END) AS very_poor_days
FROM daily_readings
GROUP BY city
ORDER BY severe_days + very_poor_days DESC;
-- Insight: Quantifies the most hazardous days experienced.

-- 6. Percentage of days exceeding CPCB (NAAQS) limits per city
/* Limits: PM2.5 > 60 µg/m³, PM10 > 100 µg/m³ */
SELECT city,
       COUNT(*) FILTER (WHERE pm25 > 60 OR pm10 > 100)::decimal / COUNT(*) * 100 AS exceed_pct
FROM daily_readings
GROUP BY city
ORDER BY exceed_pct DESC;
-- Insight: Shows compliance gaps with national standards.

-- 7. Dominant pollutant by city (pollutant with highest average concentration)
WITH pollutant_avg AS (
    SELECT city,
           UNNEST(ARRAY['pm25','pm10','no','no2','nox','nh3','co','so2','o3','benzene','toluene','xylene']) AS pollutant,
           AVG(CASE WHEN UNNEST = 'pm25' THEN pm25
                    WHEN UNNEST = 'pm10' THEN pm10
                    WHEN UNNEST = 'no' THEN no
                    WHEN UNNEST = 'no2' THEN no2
                    WHEN UNNEST = 'nox' THEN nox
                    WHEN UNNEST = 'nh3' THEN nh3
                    WHEN UNNEST = 'co' THEN co
                    WHEN UNNEST = 'so2' THEN so2
                    WHEN UNNEST = 'o3' THEN o3
                    WHEN UNNEST = 'benzene' THEN benzene
                    WHEN UNNEST = 'toluene' THEN toluene
                    WHEN UNNEST = 'xylene' THEN xylene END) AS avg_conc
    FROM daily_readings
    GROUP BY city, pollutant
)
SELECT city, pollutant, avg_conc
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY city ORDER BY avg_conc DESC) AS rn
    FROM pollutant_avg
) sub
WHERE rn = 1;
-- Insight: Identifies the most problematic pollutant for each city.

-- 8. Effect of COVID‑19 lockdown (24 Mar – 31 May 2020)
/* Compare average AQI pre‑lockdown, during, and post‑lockdown */
WITH lockdown AS (
    SELECT date,
           aqi,
           CASE WHEN date BETWEEN '2020-03-24' AND '2020-05-31' THEN 'lockdown'
                WHEN date < '2020-03-24' THEN 'pre_lockdown'
                ELSE 'post_lockdown'
           END AS period
    FROM daily_readings
    WHERE EXTRACT(YEAR FROM date) = 2020
)
SELECT period,
       AVG(aqi) AS avg_aqi
FROM lockdown
GROUP BY period;
-- Insight: Demonstrates air quality improvement during the lockdown.

-- 9. Year‑over‑Year AQI change per city using LAG (2020 vs 2019)
WITH yearly AS (
    SELECT city,
           EXTRACT(YEAR FROM date) AS yr,
           AVG(aqi) AS avg_aqi
    FROM daily_readings
    GROUP BY city, yr
    HAVING yr IN (2019,2020)
)
SELECT city,
       2020 AS yr,
       y2020.avg_aqi AS aqi_2020,
       y2019.avg_aqi AS aqi_2019,
       ((y2020.avg_aqi - y2019.avg_aqi)/y2019.avg_aqi)*100 AS pct_change
FROM yearly y2020
JOIN yearly y2019 ON y2020.city = y2019.city AND y2020.yr = 2020 AND y2019.yr = 2019
ORDER BY pct_change DESC;
-- Insight: Quantifies how AQI shifted year‑over‑year.

-- 10. Weekday vs weekend pollution
SELECT CASE WHEN EXTRACT(ISODOW FROM date) < 6 THEN 'Weekday' ELSE 'Weekend' END AS day_type,
       AVG(aqi) AS avg_aqi
FROM daily_readings
GROUP BY day_type;
-- Insight: Reveals whether traffic‑related emissions raise weekday AQI.

-- 11. Top 10 most polluted stations (by average AQI)
SELECT station_name,
       city,
       AVG(aqi) AS avg_aqi
FROM daily_readings
GROUP BY station_name, city
ORDER BY avg_aqi DESC
LIMIT 10;
-- Insight: Highlights hotspots at a finer granularity.

-- 12. Cities with biggest improvement from 2015 to 2020
WITH yearly AS (
    SELECT city,
           EXTRACT(YEAR FROM date) AS yr,
           AVG(aqi) AS avg_aqi
    FROM daily_readings
    GROUP BY city, yr
    HAVING yr IN (2015,2020)
)
SELECT y2020.city,
       y2015.avg_aqi AS aqi_2015,
       y2020.avg_aqi AS aqi_2020,
       (y2015.avg_aqi - y2020.avg_aqi) AS improvement
FROM yearly y2020
JOIN yearly y2015 ON y2020.city = y2015.city AND y2020.yr = 2020 AND y2015.yr = 2015
ORDER BY improvement DESC
LIMIT 10;
-- Insight: Shows which cities made the most progress.

-- 13. Diwali / Oct‑Nov stubble‑burning impact (focus on Delhi and North India)
/* Compare AQI in Oct‑Nov of 2019 vs 2020 */
WITH diwali AS (
    SELECT EXTRACT(YEAR FROM date) AS yr,
           AVG(aqi) AS avg_aqi
    FROM daily_readings
    WHERE city IN ('Delhi','Haryana','Punjab','Uttar Pradesh')
      AND EXTRACT(MONTH FROM date) IN (10,11)
    GROUP BY yr
)
SELECT yr, avg_aqi FROM diwali ORDER BY yr;
-- Insight: Shows any reduction/increase during typical stubble‑burning months.

-- 14. State‑wise ranking using DENSE_RANK on average AQI
SELECT state,
       AVG(aqi) AS avg_aqi,
       DENSE_RANK() OVER (ORDER BY AVG(aqi) DESC) AS rank_desc
FROM daily_readings
GROUP BY state
ORDER BY rank_desc;
-- Insight: Provides a clear hierarchy of states by pollution.

-- 15. Running cumulative count of bad‑air days per city (AQI > 150)
SELECT city,
       date,
       SUM(CASE WHEN aqi > 150 THEN 1 ELSE 0 END) OVER (PARTITION BY city ORDER BY date) AS cumulative_bad_days
FROM daily_readings
ORDER BY city, date;
-- Insight: Visualises how chronic poor air accumulates over time.

-- End of business queries
