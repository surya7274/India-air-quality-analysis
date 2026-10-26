# India Air Quality Analysis (2015 – 2020) & Power BI Dashboard

An end-to-end data analytics and business intelligence solution analyzing urban air pollution patterns across 26 major Indian cities over 5.5 years (2015–2020). The project includes automated ETL pipelines, feature engineering, PostgreSQL schema & analytical queries, and a production-grade **Power BI Dashboard** with native templates, PBIP project definitions, 30+ DAX measures, and an interactive browser-based dashboard simulator.

---

## 🌟 Power BI Dashboard Highlights

The project now includes a complete Power BI business intelligence suite located in [`powerbi/`](powerbi/):

1. **Native Power BI Template (`.pbit`) & Project (`.pbip`)**:
   * [`India_Air_Quality_Analysis.pbit`](powerbi/India_Air_Quality_Analysis.pbit) — Double-click to open in Power BI Desktop.
   * [`India_Air_Quality_Analysis.pbip`](powerbi/India_Air_Quality_Analysis.pbip) — Git-friendly Power BI Project format with [`model.bim`](powerbi/India_Air_Quality_Analysis.Dataset/model.bim) and [`report.json`](powerbi/India_Air_Quality_Analysis.Report/report.json).
2. **Interactive Standalone Browser Dashboard (Mac / PC / Mobile)**:
   * [`powerbi/dashboard/index.html`](powerbi/dashboard/index.html) — Open directly in Safari, Chrome, Edge, or Firefox.
   * Features dynamic slicers (City, Region, Year), real-time KPI scorecards, interactive Leaflet Map of India, multi-year time series, COVID-19 lockdown impact leaderboard, and dark/light themes.
3. **Star Schema Data Model (`powerbi/data/`)**:
   * Pre-processed, clean dimensions and fact tables (`Dim_City`, `Dim_Date`, `Dim_AQI_Category`, `Dim_Pollutant`, `Fact_Daily_Readings`, `Fact_Lockdown_Impact`).
4. **DAX Measures Library (`powerbi/dax/`)**:
   * 30+ industry-standard DAX measures in [`DAX_Measures.dax`](powerbi/dax/DAX_Measures.dax) and documented in [`DAX_Measures_Reference.md`](powerbi/dax/DAX_Measures_Reference.md).
5. **Power Query (M) Scripts**:
   * Automated ETL and type transforms in [`powerbi/scripts/PowerQuery_M_Script.m`](powerbi/scripts/PowerQuery_M_Script.m).

---

## 📊 Dashboard Visual Structure (5 Pages)

| Page | Key Visuals & Analytical Focus | Addressed Business Queries |
|---|---|---|
| **1. Executive Overview** | KPI cards (Avg AQI, Total Days, % Hazardous, % NAAQS Exceedance), CPCB Category Donut Chart, Top 15 Most Polluted Cities Bar Chart, Multi-Year AQI Trajectory. | Query 1, 2, 5, 6 |
| **2. Geographical & Regional** | Interactive India Bubble Map (latitude/longitude, size = AQI, color = CPCB category), Regional Comparison (North, South, East, West, Central, North East), State Hierarchy (`DENSE_RANK`). | Query 1, 2, 11, 14 |
| **3. Temporal & Seasonal** | Seasonal pollution variation (Winter vs Monsoon), October–November Stubble Burning & Diwali Surge for Gangetic plain cities, Weekday vs Weekend traffic emission deltas. | Query 3, 4, 10, 13 |
| **4. COVID-19 Lockdown Impact** | Natural experiment evaluation: Pre-lockdown vs Lockdown vs Post-lockdown AQI, City-by-city % reduction leaderboard, $PM_{2.5}$ drop vs $NO_2$ drop scatter. | Query 8, 9 |
| **5. Pollutant Deep Dive & NCAP** | Dominant pollutant distribution, $PM_{2.5}$ to $PM_{10}$ fine ratio source attribution (combustion vs crustal dust), All-city regulatory non-compliance table. | Query 7, 12, 15 |

---

## 🚀 Quick Start Guide

### 1. View Interactive Dashboard (Instant, Any OS)
Open [`powerbi/dashboard/index.html`](powerbi/dashboard/index.html) in your browser:
```bash
# Optional: serve locally
cd powerbi/dashboard
python3 -m http.server 8080
# Open http://localhost:8080
```

### 2. Open in Power BI Desktop (Windows)
* Double-click [`powerbi/India_Air_Quality_Analysis.pbit`](powerbi/India_Air_Quality_Analysis.pbit) or open [`powerbi/India_Air_Quality_Analysis.pbip`](powerbi/India_Air_Quality_Analysis.pbip) directly in Power BI Desktop.
* Connect the data folder to `powerbi/data/`.

### 3. Run Data Pipelines from Scratch
```bash
# Clean raw data
python3 src/clean_data.py

# Compute features & rolling averages
python3 src/feature_engineering.py

# Generate Power BI Star Schema datasets
python3 src/prepare_powerbi_data.py

# Generate Web Dashboard data & files
python3 src/generate_dashboard_data.py
python3 src/generate_html_dashboard.py
python3 src/package_pbit.py
```

---

## 📈 Key Findings from the Data

* **National AQI Average:** Over 29,531 daily readings across 26 cities, the average AQI is **176.4** (*Moderate* category).
* **Most Polluted Cities:** **Ahmedabad** (avg AQI 452.1) and **Delhi** (avg AQI 259.5) consistently experience the highest number of *Severe* and *Very Poor* air quality days.
* **Cleanest Cities:** **Aizawl** (avg AQI 34.8), **Shillong** (avg AQI 53.8), and **Thiruvananthapuram** (avg AQI 75.8) enjoy relatively clean air compliant with WHO guidelines.
* **Winter Inversion Peak:** Winter (Dec–Feb) average AQI is **220.6**, compared to **88.2** during the Monsoon (Jun–Aug) — a **2.5x seasonal surge**.
* **COVID-19 Lockdown Impact (2020):** National quarantine (Mar 24 – May 31, 2020) triggered a **41.4% drop in average AQI** across all 26 cities:
  * **Ahmedabad:** 394.7 $\rightarrow$ 129.3 (**-67.2%**)
  * **Delhi:** 249.6 $\rightarrow$ 125.4 (**-49.8%**, $PM_{2.5}$ dropped **-59.2%**, $NO_2$ dropped **-50.8%**)
  * **Kolkata:** 168.2 $\rightarrow$ 87.1 (**-48.2%**)

---

## 📂 Repository Structure

```
India-air-quality-analysis/
├── powerbi/
│   ├── India_Air_Quality_Analysis.pbit          # Power BI Template
│   ├── India_Air_Quality_Analysis.pbip          # Power BI Project File
│   ├── India_Air_Quality_Analysis.Report/       # Visuals & layout definition
│   ├── India_Air_Quality_Analysis.Dataset/      # Tabular model (model.bim)
│   ├── POWER_BI_DASHBOARD_GUIDE.md              # Detailed implementation guide
│   ├── data/                                    # Star Schema Data Model CSVs
│   │   ├── Dim_City.csv
│   │   ├── Dim_Date.csv
│   │   ├── Dim_AQI_Category.csv
│   │   ├── Dim_Pollutant.csv
│   │   ├── Fact_Daily_Readings.csv
│   │   ├── Fact_City_Monthly_Summary.csv
│   │   └── Fact_Lockdown_Impact.csv
│   ├── dax/
│   │   ├── DAX_Measures.dax                     # 30+ DAX measures
│   │   └── DAX_Measures_Reference.md            # DAX reference guide
│   ├── scripts/
│   │   └── PowerQuery_M_Script.m                # Automated Power Query M code
│   └── dashboard/
│       ├── index.html                           # Standalone Interactive Web Dashboard
│       └── dashboard_data.json                  # Clean JSON data
├── src/
│   ├── clean_data.py                            # Missing value imputation & cleaning
│   ├── feature_engineering.py                   # Derived ratios, rolling windows, categories
│   ├── compute_insights.py                      # Core statistical benchmarks
│   ├── prepare_powerbi_data.py                  # Generates Star Schema tables
│   ├── generate_pbip.py                         # Generates PBIP files
│   ├── package_pbit.py                          # Compiles .pbit template
│   └── generate_html_dashboard.py               # Compiles web dashboard
├── sql/
│   ├── schema.sql                               # PostgreSQL relational schema
│   └── business_queries.sql                     # 15 Analytical business queries
└── README.md
```
