# Power BI Dashboard Implementation & Architecture Guide
## India Air Quality Analysis (2015 – 2020)

This guide provides complete technical documentation, data modeling blueprints, visual wireframes, and step-by-step instructions for deploying and interacting with the Power BI Dashboard for the India Air Quality project.

---

## 1. Project & Dashboard Architecture

```
                          ┌──────────────────────────┐
                          │   Raw CPCB Daily Data    │
                          │   (29,531 daily records) │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │    ETL & Data Prep       │
                          │(clean_data, feature_eng) │
                          └─────────────┬────────────┘
                                        │
                ┌───────────────────────┴───────────────────────┐
                ▼                                               ▼
   ┌──────────────────────────┐                   ┌──────────────────────────┐
   │    Star Schema Tables    │                   │   Power BI Modeling      │
   │   - Dim_City             │                   │   - model.bim / .pbip    │
   │   - Dim_Date             │                   │   - .pbit Template       │
   │   - Dim_AQI_Category     │                   │   - 30+ DAX Measures     │
   │   - Dim_Pollutant        │                   │   - Power Query (M)      │
   │   - Fact_Daily_Readings  │                   └─────────────┬────────────┘
   │   - Fact_Lockdown_Impact │                                 │
   └────────────┬─────────────┘                                 ▼
                │                                 ┌──────────────────────────┐
                ▼                                 │ Power BI Desktop/Service │
   ┌──────────────────────────┐                   │ (5 Interactive Pages)    │
   │ Interactive Web Dashboard│                   └──────────────────────────┘
   │ (powerbi/dashboard/)     │
   │ - Full Mac/PC/Browser    │
   │ - Slicers, Map, Charts   │
   └──────────────────────────┘
```

---

## 2. Power BI Star Schema Data Model

The data model is structured around a Star Schema optimized for high-performance aggregation and filtering across 26 cities and 5.5 years of measurements.

### Model Relationships:
1. **`Fact_Daily_Readings[City]` $\rightarrow$ `Dim_City[City]`**
   * *Cardinality:* Many-to-One (`* : 1`)
   * *Cross-filter direction:* Single
2. **`Fact_Daily_Readings[Date]` $\rightarrow$ `Dim_Date[Date]`**
   * *Cardinality:* Many-to-One (`* : 1`)
   * *Cross-filter direction:* Single
3. **`Fact_Daily_Readings[AQI_Category]` $\rightarrow$ `Dim_AQI_Category[Category_Name]`**
   * *Cardinality:* Many-to-One (`* : 1`)
   * *Cross-filter direction:* Single
4. **`Fact_Lockdown_Impact[City]` $\rightarrow$ `Dim_City[City]`**
   * *Cardinality:* Many-to-One (`* : 1`)
   * *Cross-filter direction:* Single

---

## 3. How to Open and Use the Dashboard

### Option A: Instant Interactive Browser Dashboard (macOS & All Platforms)
Because Power BI Desktop is native to Windows, a fully interactive Power BI web simulator is provided inside this repository:
1. Navigate to: `powerbi/dashboard/index.html`
2. Double-click the file or open it in any browser (Safari, Chrome, Firefox, Edge).
3. Alternatively, launch a local web server:
   ```bash
   cd powerbi/dashboard
   python3 -m http.server 8080
   ```
   Open `http://localhost:8080` in your browser.
4. **Features available:**
   * Dynamic slicers for **City**, **Region**, and **Year**.
   * Real-time calculated KPI cards with CPCB color indicators.
   * Interactive Leaflet Map of India with color-coded circles and popups.
   * Multi-year time series, seasonal charts, and COVID-19 lockdown impact analysis.
   * Dark Mode / Light Mode toggle and CSV summary export.

### Option B: Power BI Desktop via Template (`.pbit`)
1. On a Windows machine with Power BI Desktop installed, navigate to:
   `powerbi/India_Air_Quality_Analysis.pbit`
2. Double-click to open. Power BI Desktop will automatically unpack the model, relationships, and layout.
3. If prompted for data location, provide the absolute path to `powerbi/data/`.

### Option C: Modern Power BI Project (`.pbip`)
1. Open Power BI Desktop (File $\rightarrow$ Open report).
2. Select: `powerbi/India_Air_Quality_Analysis.pbip`
3. This format is git-friendly and exposes source JSON definitions (`report.json` and `model.bim`).

### Option D: Manual Import via Power Query M
If you prefer creating a custom report from scratch:
1. Open Power BI Desktop $\rightarrow$ **Transform Data** (Power Query Editor).
2. Create a Text Parameter named `DataFolderPath` set to the directory containing your CSVs (`.../powerbi/data`).
3. Click **New Source $\rightarrow$ Blank Query $\rightarrow$ Advanced Editor**.
4. Paste the queries provided in [powerbi/scripts/PowerQuery_M_Script.m](scripts/PowerQuery_M_Script.m).

---

## 4. Dashboard Report Pages & Visual Mapping

The dashboard contains 5 dedicated pages addressing all 15 business queries from the project:

### Page 1: Executive Overview
* **Dynamic Slicers (Top Ribbon):** City, Region, Year.
* **KPI Scorecard Cards:**
  * Average AQI (with dynamic color badge and CPCB health advisory)
  * Total Daily Readings (29,531 observations across 26 cities)
  * Hazardous Days Count & % (Severe + Very Poor)
  * NAAQS Exceedance Rate (CPCB national standard breach rate)
  * COVID-19 Lockdown Average Reduction (-41.4% national drop)
* **Visual 1 (Donut Chart):** CPCB Category Distribution (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).
* **Visual 2 (Horizontal Bar Chart):** Top 10 Most Polluted vs Cleanest Cities benchmarked against national standards.
* **Visual 3 (Line Chart):** Multi-Year Monthly AQI Trajectory (2015 to 2020) revealing winter peaks and the COVID dip.

### Page 2: Geographical & Regional Intelligence
* **Visual 1 (Bubble Map):** India Map with coordinates for all 26 cities.
  * *Latitude:* `Dim_City[Latitude]`, *Longitude:* `Dim_City[Longitude]`
  * *Bubble Size:* `Fact_Daily_Readings[Average AQI]`
  * *Bubble Color:* CPCB Category color
* **Visual 2 (Bar Chart):** Regional AQI Comparison (Northern, Western, Eastern, Central, Southern, North Eastern).
* **Visual 3 (Interactive Table):** State Pollution Hierarchy using `DENSE_RANK()` (Business Query 14).

### Page 3: Temporal & Seasonal Patterns
* **Visual 1 (Bar Chart):** Seasonal Pollution Variation (Winter vs Spring vs Summer vs Monsoon vs Post-monsoon).
  * *Insight:* Demonstrates winter inversion where AQI is 2.5x to 3x higher than monsoon washout.
* **Visual 2 (Clustered Column Chart):** October–November Stubble Burning & Diwali Surge for Delhi, Amritsar, Lucknow, and Patna (Business Query 13).
* **Visual 3 (Column Chart):** Weekday vs Weekend Traffic Emission variations (Business Query 10).

### Page 4: COVID-19 Lockdown Impact (Natural Experiment)
* **Visual 1 (Horizontal Bar):** City-by-City Lockdown AQI % Reduction Leaderboard (Business Query 8).
  * Highlights Ahmedabad (-67.2%), Delhi (-49.8%), Kolkata (-48.2%), Bengaluru (-26.1%).
* **Visual 2 (Clustered Column):** Pre-Lockdown AQI vs Lockdown AQI by City.
* **Visual 3 (Scatter Plot):** $PM_{2.5}$ Reduction % vs $NO_2$ Reduction % (distinguishing vehicular vs industrial drops).
* **Visual 4 (Data Matrix):** Detailed lockdown metrics with before/during/after delta points.

### Page 5: Pollutant Deep Dive & NCAP Compliance
* **Visual 1 (Pie Chart):** Dominant Pollutant Breakdown (PM2.5, PM10, NO2, SO2, CO, O3) (Business Query 7).
* **Visual 2 (Bar Chart):** $PM_{2.5}$ to $PM_{10}$ Fine Ratio by City.
  * *Analysis:* Ratio $\ge 0.60$ flags combustion and vehicular smoke; $< 0.45$ flags windblown road dust.
* **Visual 3 (Summary Table):** Complete city compliance matrix with CPCB NAAQS and WHO exceedance rates (Business Query 6).

---

## 5. CPCB Standard Colors & Thresholds

Use these exact hex codes in Power BI conditional formatting:

| Category | AQI Range | Color Name | Hex Code | Public Health Impact |
|---|---|---|---|---|
| **Good** | 0 – 50 | Green | `#00E400` | Minimal impact; clean air. |
| **Satisfactory** | 51 – 100 | Light Green | `#92D050` | Minor breathing discomfort to sensitive people. |
| **Moderate** | 101 – 200 | Yellow | `#FFFF00` | Breathing discomfort to people with asthma or lung disease. |
| **Poor** | 201 – 300 | Orange | `#FF7E00` | Breathing discomfort to most people on prolonged exposure. |
| **Very Poor** | 301 – 400 | Red | `#FF0000` | Respiratory illness on prolonged exposure. |
| **Severe** | 401+ | Maroon | `#7E0023` | Affects healthy people; severe impact on vulnerable groups. |

---

## 6. Project Directory Reference

```
India-air-quality-analysis/
├── powerbi/
│   ├── India_Air_Quality_Analysis.pbit          # Power BI Template
│   ├── India_Air_Quality_Analysis.pbip          # Power BI Project File
│   ├── India_Air_Quality_Analysis.Report/       # Report visuals & layout JSON
│   ├── India_Air_Quality_Analysis.Dataset/      # Tabular model (model.bim)
│   ├── data/                                    # Star Schema CSVs
│   │   ├── Dim_City.csv
│   │   ├── Dim_Date.csv
│   │   ├── Dim_AQI_Category.csv
│   │   ├── Dim_Pollutant.csv
│   │   ├── Fact_Daily_Readings.csv
│   │   ├── Fact_City_Monthly_Summary.csv
│   │   └── Fact_Lockdown_Impact.csv
│   ├── dax/                                     # DAX Measures & Reference
│   │   ├── DAX_Measures.dax
│   │   └── DAX_Measures_Reference.md
│   ├── scripts/                                 # Power Query M Code
│   │   └── PowerQuery_M_Script.m
│   └── dashboard/                               # Standalone Interactive Dashboard
│       ├── index.html                           # Browser application (Mac/PC)
│       └── dashboard_data.json                  # Clean pre-aggregated JSON
├── src/                                         # Data Pipelines
│   ├── clean_data.py
│   ├── feature_engineering.py
│   ├── compute_insights.py
│   ├── prepare_powerbi_data.py
│   ├── generate_pbip.py
│   ├── package_pbit.py
│   └── generate_html_dashboard.py
└── sql/
    ├── schema.sql
    └── business_queries.sql
```
