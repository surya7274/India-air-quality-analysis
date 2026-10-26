# Power BI DAX Measures Reference Guide

This document catalogs all DAX measures developed for the **India Air Quality Analysis (2015–2020)** Power BI dashboard.
Each measure is aligned directly with the Central Pollution Control Board (CPCB) standards and the project's SQL business queries.

---

## 1. Executive Summary & AQI Measures

| Measure Name | DAX Expression | Intended Visual | Description |
|---|---|---|---|
| **`[Total Readings]`** | `COUNTROWS(Fact_Daily_Readings)` | Card | Total days of air quality data recorded (29,531 records). |
| **`[Total Cities Monitored]`** | `DISTINCTCOUNT(Fact_Daily_Readings[City])` | Card | Number of Indian cities analyzed (26). |
| **`[Average AQI]`** | `AVERAGE(Fact_Daily_Readings[AQI])` | Card, Gauge, Map Bubble Size | Weighted/average Air Quality Index over active filters. |
| **`[Median AQI]`** | `MEDIAN(Fact_Daily_Readings[AQI])` | Tooltip, Card | Robust central tendency metric less affected by extreme winter spikes. |
| **`[Max AQI]`** | `MAX(Fact_Daily_Readings[AQI])` | Tooltip | Peak observed pollution index. |
| **`[AQI KPI Status Color]`** | *Conditional Hex String (`#00E400` to `#7E0023`)* | Conditional Formatting (Background) | Dynamically tints cards and chart data points according to CPCB thresholds. |
| **`[AQI Health Status]`** | *Text label based on CPCB categories* | Sub-card / Callout text | Displays advisory (e.g., *"Good - Clean Air"* vs *"Severe - Emergency Alert"*). |

---

## 2. Regulatory Compliance & Hazard Metrics (CPCB & WHO)

| Measure Name | DAX Expression | Intended Visual | Description |
|---|---|---|---|
| **`[Severe Days Count]`** | `CALCULATE(COUNTROWS(...), Fact_Daily_Readings[AQI_Category] = "Severe")` | Card / Bar Chart | Total days with AQI > 400 (Severe risk). Addresses Business Query 5. |
| **`[Very Poor Days Count]`** | `CALCULATE(..., Fact_Daily_Readings[AQI_Category] = "Very Poor")` | Card / Bar Chart | Total days with AQI 301–400. |
| **`[Hazardous Days Count]`** | `[Severe Days Count] + [Very Poor Days Count]` | Card, Donut Chart | Combined critical pollution days. |
| **`[% Hazardous Days]`** | `DIVIDE([Hazardous Days Count], [Total Readings], 0)` | KPI Card / Gauge | Proportion of days unsafe for public outdoor exposure. |
| **`[% NAAQS Exceedance Rate]`** | `DIVIDE([NAAQS Exceed Days Count], [Total Readings], 0)` | Bar Chart, Scatter | % days exceeding CPCB 24-hr standards ($PM_{2.5} > 60$ or $PM_{10} > 100\ \mu g/m^3$). Addresses Business Query 6. |
| **`[% WHO Exceedance Rate]`** | `DIVIDE([WHO Exceed Days Count], [Total Readings], 0)` | Card / Comparison | % days exceeding strict WHO guideline ($PM_{2.5} > 15\ \mu g/m^3$). |
| **`[Chronic Bad Days Count]`** | `CALCULATE(..., Fact_Daily_Readings[AQI] > 150)` | Area Chart | Cumulative bad-air days tracker. Addresses Business Query 15. |
| **`[Cumulative Bad Days Running Total]`** | `CALCULATE([Chronic Bad Days Count], FILTER(ALLSELECTED(...)))` | Line Chart (Cumulative) | Chronic pollution buildup curve over time. |

---

## 3. Time Intelligence & Seasonality Measures

| Measure Name | DAX Expression | Intended Visual | Description |
|---|---|---|---|
| **`[AQI Previous Year]`** | `CALCULATE([Average AQI], SAMEPERIODLASTYEAR(Dim_Date[Date]))` | Line Chart / Tooltip | Prior year baseline comparison using Time Intelligence. |
| **`[AQI YoY % Change]`** | `DIVIDE([Average AQI] - [AQI Previous Year], [AQI Previous Year])` | KPI Card Indicator | Year-over-Year % improvement or worsening. Addresses Business Query 3 & 9. |
| **`[Dynamic Rolling 7D AQI]`** | `CALCULATE(AVERAGE(...), DATESINPERIOD(..., -7, DAY))` | Line Chart | Short-term smoothed air quality trend. |
| **`[Dynamic Rolling 30D AQI]`** | `CALCULATE(AVERAGE(...), DATESINPERIOD(..., -30, DAY))` | Line Chart | Monthly moving baseline. |
| **`[Winter Avg AQI]`** | `CALCULATE([Average AQI], Dim_Date[Season] = "Winter")` | Matrix, Column Chart | Winter pollution level (Dec, Jan, Feb). Addresses Business Query 4. |
| **`[Monsoon Avg AQI]`** | `CALCULATE([Average AQI], Dim_Date[Season] = "Monsoon")` | Matrix, Column Chart | Monsoon rain washout level (Jun, Jul, Aug). |
| **`[Seasonal Pollution Ratio]`** | `DIVIDE([Winter Avg AQI], [Monsoon Avg AQI], 0)` | Card | Multiplier showing how much dirtier winter is than monsoon. |
| **`[Stubble Burning Oct-Nov AQI]`**| `CALCULATE([Average AQI], Dim_Date[Month] IN {10, 11})` | Trend / Callout | Stubble-burning and post-harvest smog spike indicator. Addresses Business Query 13. |
| **`[Weekday vs Weekend Diff]`** | `[Weekday Avg AQI] - [Weekend Avg AQI]` | KPI Card | Traffic/industrial emission delta between weekdays and weekends. Addresses Business Query 10. |

---

## 4. COVID-19 Lockdown Natural Experiment Measures

| Measure Name | DAX Expression | Intended Visual | Description |
|---|---|---|---|
| **`[2020 Pre-Lockdown AQI]`** | `CALCULATE(..., Dim_Date[Date] < DATE(2020,3,24))` | Clustered Column | Baseline before national lockdown. Addresses Business Query 8. |
| **`[2020 Lockdown AQI]`** | `CALCULATE(..., DATE(2020,3,24) TO DATE(2020,5,31))` | Clustered Column | Period of strict quarantine and vehicle stoppage. |
| **`[2020 Post-Lockdown AQI]`** | `CALCULATE(..., Dim_Date[Date] > DATE(2020,5,31))` | Clustered Column | Gradual reopening and monsoon period. |
| **`[% Lockdown AQI Reduction]`** | `DIVIDE([Pre] - [Lock], [Pre])` | Horizontal Bar / Card | % AQI drop during lockdown (averages ~41% nationally). |
| **`[% Lockdown PM2.5 Reduction]`**| `DIVIDE([Pre PM2.5] - [Lock PM2.5], [Pre PM2.5])` | Waterfall / Bar Chart | Drop in fine inhalable combustion particles. |
| **`[% Lockdown NO2 Reduction]`** | `DIVIDE([Pre NO2] - [Lock NO2], [Pre NO2])` | Bar Chart | Drop in vehicle-exhaust indicator gas ($NO_2$). |

---

## 5. Particle Physics & Source Attribution

| Measure Name | DAX Expression | Intended Visual | Description |
|---|---|---|---|
| **`[PM2.5 to PM10 Fine Ratio]`**| `DIVIDE([Average PM2.5], [Average PM10], 0)` | Gauge / Scatter | Ratio between fine combustion particles and total suspended particulates. |
| **`[Particle Source Dominance]`**| *Conditional Text* | Dynamic Text | Identifies whether pollution is driven by combustion/traffic ($\ge 0.60$) or road dust ($< 0.45$). |
| **`[City AQI Rank]`** | `RANKX(ALLSELECTED(Dim_City[City]), [Average AQI], , DESC, Dense)` | Table / Leaderboard | Dynamic ranking of cities from most to least polluted. Addresses Business Query 1 & 2. |
| **`[State AQI Rank]`** | `RANKX(ALLSELECTED(Dim_City[State]), [Average AQI], , DESC, Dense)` | Table / Treemap | State-level pollution hierarchy. Addresses Business Query 14. |
| **`[Cleanest 5-Year Improvement]`**| `AQI 2015 - AQI 2020` | Leaderboard | Cities with the greatest progress over 5 years. Addresses Business Query 12. |
