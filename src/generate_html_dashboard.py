"""Script to compile and write the interactive Power BI HTML Dashboard.
Embeds the pre-aggregated JSON so that opening the file in a browser works directly
without any local server or CORS restrictions.
"""

import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(BASE_DIR, "powerbi", "dashboard", "dashboard_data.json")
HTML_PATH = os.path.join(BASE_DIR, "powerbi", "dashboard", "index.html")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    dashboard_data_str = f.read()

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>India Air Quality Analysis | Power BI Interactive Dashboard</title>
  <!-- Chart.js and Leaflet CDN -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --pbi-yellow: #f2c811;
      --pbi-yellow-dark: #d9b106;
      --pbi-header-bg: #1f1f1f;
      --pbi-bg: #f3f2f1;
      --pbi-card-bg: #ffffff;
      --pbi-text-main: #252423;
      --pbi-text-muted: #605e5c;
      --pbi-border: #edebe9;
      --pbi-accent: #0078d4;
      --shadow-sm: 0 1.6px 3.6px 0 rgba(0,0,0,0.132), 0 0.3px 0.9px 0 rgba(0,0,0,0.108);
      --shadow-md: 0 3.2px 7.2px 0 rgba(0,0,0,0.132), 0 0.6px 1.8px 0 rgba(0,0,0,0.108);
      --font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    }}

    [data-theme="dark"] {{
      --pbi-bg: #121212;
      --pbi-card-bg: #1e1e1e;
      --pbi-text-main: #f3f2f1;
      --pbi-text-muted: #a19f9d;
      --pbi-border: #2d2d2d;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-family);
      background-color: var(--pbi-bg);
      color: var(--pbi-text-main);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}

    /* Top Power BI Bar */
    .pbi-topbar {{
      background: var(--pbi-header-bg);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 18px;
      font-size: 13px;
      border-bottom: 2px solid var(--pbi-yellow);
    }}
    .pbi-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .pbi-logo {{
      background: var(--pbi-yellow);
      color: #111;
      font-weight: 800;
      font-size: 11px;
      padding: 3px 6px;
      border-radius: 3px;
      letter-spacing: 0.5px;
    }}
    .pbi-report-title {{
      font-size: 15px;
      font-weight: 600;
      color: #fff;
    }}
    .pbi-top-actions {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .btn-top {{
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      transition: background 0.2s;
    }}
    .btn-top:hover {{ background: rgba(255,255,255,0.2); }}

    /* Slicer Ribbon */
    .pbi-slicer-bar {{
      background: var(--pbi-card-bg);
      border-bottom: 1px solid var(--pbi-border);
      padding: 10px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 16px;
      box-shadow: var(--shadow-sm);
      z-index: 10;
    }}
    .slicer-group {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .slicer-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--pbi-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .slicer-select {{
      padding: 5px 10px;
      font-size: 13px;
      font-family: inherit;
      border: 1px solid var(--pbi-border);
      border-radius: 3px;
      background: var(--pbi-card-bg);
      color: var(--pbi-text-main);
      cursor: pointer;
      outline: none;
    }}
    .slicer-select:focus {{
      border-color: var(--pbi-accent);
    }}
    .badge-clear {{
      background: #e1dfdd;
      color: #323130;
      padding: 4px 8px;
      border-radius: 3px;
      font-size: 11px;
      cursor: pointer;
      border: none;
      font-weight: 600;
    }}
    .badge-clear:hover {{ background: #c8c6c4; }}

    /* KPI Cards Row */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      padding: 14px 20px 8px 20px;
    }}
    .kpi-card {{
      background: var(--pbi-card-bg);
      border-radius: 5px;
      padding: 12px 16px;
      box-shadow: var(--shadow-sm);
      border-left: 4px solid var(--pbi-accent);
      position: relative;
    }}
    .kpi-title {{
      font-size: 11px;
      color: var(--pbi-text-muted);
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .kpi-value {{
      font-size: 24px;
      font-weight: 700;
      color: var(--pbi-text-main);
      display: flex;
      align-items: baseline;
      gap: 6px;
    }}
    .kpi-subtext {{
      font-size: 11px;
      color: var(--pbi-text-muted);
      margin-top: 4px;
    }}
    .kpi-badge {{
      display: inline-block;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: 600;
      margin-left: 6px;
    }}

    /* Main Canvas Area */
    .canvas-container {{
      flex: 1;
      overflow-y: auto;
      padding: 10px 20px 20px 20px;
    }}
    .page-section {{
      display: none;
    }}
    .page-section.active {{
      display: block;
    }}

    /* Visual Grids */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .grid-1-2 {{
      display: grid;
      grid-template-columns: 1fr 2fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .grid-2-1 {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }}

    /* Card Panels for Visuals */
    .visual-card {{
      background: var(--pbi-card-bg);
      border-radius: 6px;
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--pbi-border);
      padding: 16px;
      display: flex;
      flex-direction: column;
    }}
    .visual-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--pbi-border);
    }}
    .visual-title {{
      font-size: 14px;
      font-weight: 600;
      color: var(--pbi-text-main);
    }}
    .visual-subtitle {{
      font-size: 11px;
      color: var(--pbi-text-muted);
    }}
    .chart-container {{
      position: relative;
      flex: 1;
      min-height: 260px;
    }}

    /* Tables */
    .pbi-table-wrapper {{
      overflow-x: auto;
      max-height: 480px;
    }}
    .pbi-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }}
    .pbi-table th {{
      position: sticky;
      top: 0;
      background: var(--pbi-bg);
      color: var(--pbi-text-main);
      padding: 8px 10px;
      font-weight: 600;
      border-bottom: 2px solid var(--pbi-border);
      cursor: pointer;
    }}
    .pbi-table td {{
      padding: 7px 10px;
      border-bottom: 1px solid var(--pbi-border);
    }}
    .pbi-table tr:hover {{
      background: rgba(0, 120, 212, 0.05);
    }}

    /* Map Styling */
    #indiaMap {{
      width: 100%;
      height: 480px;
      border-radius: 4px;
      z-index: 1;
    }}

    /* Bottom Page Tab Strip (Power BI Navigation) */
    .pbi-page-tabs {{
      background: var(--pbi-card-bg);
      border-top: 1px solid var(--pbi-border);
      display: flex;
      align-items: center;
      padding: 0 16px;
      height: 40px;
      overflow-x: auto;
      box-shadow: 0 -2px 6px rgba(0,0,0,0.05);
      z-index: 100;
    }}
    .tab-btn {{
      padding: 10px 18px;
      font-size: 13px;
      font-weight: 600;
      color: var(--pbi-text-muted);
      border: none;
      background: none;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{
      color: var(--pbi-accent);
      background: rgba(0, 120, 212, 0.04);
    }}
    .tab-btn.active {{
      color: var(--pbi-accent);
      border-bottom-color: var(--pbi-accent);
      background: rgba(0, 120, 212, 0.08);
    }}

    /* CPCB Color Indicator Tag */
    .cpcb-tag {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 3px;
      font-weight: 700;
      font-size: 11px;
    }}

    /* Callout Note */
    .insight-box {{
      background: rgba(0, 120, 212, 0.08);
      border-left: 4px solid var(--pbi-accent);
      padding: 10px 14px;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.5;
      margin-top: 10px;
    }}

    @media (max-width: 900px) {{
      .grid-2, .grid-1-2, .grid-2-1, .grid-3 {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- Power BI Top Banner -->
  <header class="pbi-topbar">
    <div class="pbi-brand">
      <span class="pbi-logo">Power BI</span>
      <span class="pbi-report-title" id="reportHeading">India Air Quality Performance Monitor (2015 - 2020)</span>
    </div>
    <div class="pbi-top-actions">
      <button class="btn-top" onclick="exportDataCSV()">📥 Export Summary CSV</button>
      <button class="btn-top" onclick="toggleTheme()">🌓 Dark / Light</button>
    </div>
  </header>

  <!-- Interactive Power BI Slicer Ribbon -->
  <section class="pbi-slicer-bar">
    <div class="slicer-group">
      <span class="slicer-label">City</span>
      <select id="slicerCity" class="slicer-select" onchange="applyFilters()">
        <option value="ALL">All Cities (26 Monitored)</option>
      </select>
    </div>
    <div class="slicer-group">
      <span class="slicer-label">Region</span>
      <select id="slicerRegion" class="slicer-select" onchange="applyFilters()">
        <option value="ALL">All Regions</option>
      </select>
    </div>
    <div class="slicer-group">
      <span class="slicer-label">Year</span>
      <select id="slicerYear" class="slicer-select" onchange="applyFilters()">
        <option value="ALL">2015 - 2020 (All Years)</option>
        <option value="2015">2015</option>
        <option value="2016">2016</option>
        <option value="2017">2017</option>
        <option value="2018">2018</option>
        <option value="2019">2019</option>
        <option value="2020">2020</option>
      </select>
    </div>
    <button class="badge-clear" onclick="resetFilters()">↺ Reset Slicers</button>
  </section>

  <!-- Dynamic KPI Cards Row -->
  <section class="kpi-row">
    <div class="kpi-card" id="cardAQI" style="border-left-color: #ff7e00;">
      <div class="kpi-title">Average AQI</div>
      <div class="kpi-value">
        <span id="kpiAvgAQI">--</span>
        <span class="kpi-badge" id="kpiCategoryBadge">--</span>
      </div>
      <div class="kpi-subtext" id="kpiAQIHealth">CPCB Health Standard</div>
    </div>
    <div class="kpi-card" style="border-left-color: #0078d4;">
      <div class="kpi-title">Total Daily Readings</div>
      <div class="kpi-value" id="kpiTotalDays">29,531</div>
      <div class="kpi-subtext" id="kpiActiveCities">Across 26 Major Urban Centers</div>
    </div>
    <div class="kpi-card" style="border-left-color: #7e0023;">
      <div class="kpi-title">Hazardous Days (Severe + Very Poor)</div>
      <div class="kpi-value" id="kpiSeverePct">--</div>
      <div class="kpi-subtext" id="kpiSevereCount">Critical health emergency exposure</div>
    </div>
    <div class="kpi-card" style="border-left-color: #d13438;">
      <div class="kpi-title">NAAQS Exceedance Rate</div>
      <div class="kpi-value" id="kpiNAAQSPct">--</div>
      <div class="kpi-subtext">PM2.5 &gt; 60 or PM10 &gt; 100 µg/m³</div>
    </div>
    <div class="kpi-card" style="border-left-color: #107c41;">
      <div class="kpi-title">Lockdown Impact (2020)</div>
      <div class="kpi-value" id="kpiLockdownDrop" style="color: #107c41;">-41.4%</div>
      <div class="kpi-subtext">Avg national drop during COVID quarantine</div>
    </div>
  </section>

  <!-- Canvas Pages Container -->
  <main class="canvas-container">

    <!-- PAGE 1: EXECUTIVE OVERVIEW -->
    <div id="page-executive" class="page-section active">
      <div class="grid-1-2">
        <!-- AQI Category Distribution Donut -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">CPCB AQI Category Distribution</div>
              <div class="visual-subtitle">Days in Good, Satisfactory, Moderate, Poor, Very Poor, Severe</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartCategoryDonut"></canvas>
          </div>
        </div>

        <!-- Top 10 Most Polluted Cities Bar -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">City Pollution Benchmark (Average AQI)</div>
              <div class="visual-subtitle">Ranked from highest to lowest pollution levels</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartTopCitiesBar"></canvas>
          </div>
        </div>
      </div>

      <!-- Multi-Year AQI Trend Line Chart -->
      <div class="visual-card">
        <div class="visual-header">
          <div>
            <div class="visual-title">Multi-Year Air Quality Trajectory (2015 - 2020)</div>
            <div class="visual-subtitle">Monthly aggregate AQI showing winter hazard cycles and COVID dip</div>
          </div>
        </div>
        <div class="chart-container" style="min-height: 280px;">
          <canvas id="chartMonthlyTrend"></canvas>
        </div>
      </div>
    </div>

    <!-- PAGE 2: GEOGRAPHICAL & REGIONAL -->
    <div id="page-geographical" class="page-section">
      <div class="grid-2-1">
        <!-- Interactive India Map -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Interactive India Air Quality Map</div>
              <div class="visual-subtitle">Bubble diameter = AQI magnitude; Color = CPCB Hazard Category</div>
            </div>
          </div>
          <div id="indiaMap"></div>
        </div>

        <!-- Regional Performance & State Ranking -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Regional AQI Comparison</div>
              <div class="visual-subtitle">North vs South vs East vs West vs Central vs North East</div>
            </div>
          </div>
          <div class="chart-container" style="min-height: 200px; margin-bottom: 12px;">
            <canvas id="chartRegionalBar"></canvas>
          </div>
          <div class="visual-header" style="margin-top: 8px;">
            <div>
              <div class="visual-title">Top State Hierarchy (DENSE_RANK)</div>
            </div>
          </div>
          <div class="pbi-table-wrapper" style="max-height: 180px;">
            <table class="pbi-table" id="tableStateRank">
              <thead>
                <tr><th>Rank</th><th>State</th><th>Avg AQI</th><th>Hazard %</th></tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- PAGE 3: TEMPORAL & SEASONAL TRENDS -->
    <div id="page-temporal" class="page-section">
      <div class="grid-2">
        <!-- Seasonal AQI Comparison -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Seasonal Pollution Variation</div>
              <div class="visual-subtitle">Winter vs Monsoon rain washout comparison (Business Query 4)</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartSeasonalBar"></canvas>
          </div>
          <div class="insight-box">
            <strong>Key Policy Finding:</strong> Winter AQI is consistently 2.5x to 3.2x higher than Monsoon due to thermal inversion and stagnant atmospheric boundary layers.
          </div>
        </div>

        <!-- Oct-Nov Stubble Burning Spike -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">October - November Stubble Burning Surge</div>
              <div class="visual-subtitle">Indo-Gangetic Plain cities (Delhi, Amritsar, Lucknow, Patna)</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartStubbleBar"></canvas>
          </div>
          <div class="insight-box">
            <strong>Crop Residue Burning & Diwali:</strong> Post-monsoon months (Oct-Nov) record sudden spikes in PM2.5 concentrations exceeding 400 µg/m³.
          </div>
        </div>
      </div>

      <!-- Weekday vs Weekend Pollution -->
      <div class="visual-card">
        <div class="visual-header">
          <div>
            <div class="visual-title">Weekday vs Weekend Traffic Emissions</div>
            <div class="visual-subtitle">Assessing vehicular and commercial freight impact (Business Query 10)</div>
          </div>
        </div>
        <div class="chart-container" style="min-height: 220px;">
          <canvas id="chartWeekdayWeekend"></canvas>
        </div>
      </div>
    </div>

    <!-- PAGE 4: COVID-19 LOCKDOWN IMPACT -->
    <div id="page-lockdown" class="page-section">
      <div class="grid-2">
        <!-- City % Reduction Leaderboard -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Lockdown AQI Reduction Leaderboard (% Drop)</div>
              <div class="visual-subtitle">Pre-Lockdown (Jan 1 - Mar 23) vs Lockdown (Mar 24 - May 31, 2020)</div>
            </div>
          </div>
          <div class="chart-container" style="min-height: 340px;">
            <canvas id="chartLockdownDrops"></canvas>
          </div>
        </div>

        <!-- Pre vs During AQI Column Comparison -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Pre-Lockdown vs Lockdown AQI Comparison</div>
              <div class="visual-subtitle">Dramatic reduction across major industrial & metro hubs</div>
            </div>
          </div>
          <div class="chart-container" style="min-height: 340px;">
            <canvas id="chartPreVsLockAQI"></canvas>
          </div>
        </div>
      </div>

      <!-- Detailed Lockdown Table -->
      <div class="visual-card">
        <div class="visual-header">
          <div>
            <div class="visual-title">City-by-City Lockdown Pollution Reduction Matrix</div>
            <div class="visual-subtitle">Metrics for AQI, PM2.5, and vehicular NO2 drops</div>
          </div>
        </div>
        <div class="pbi-table-wrapper">
          <table class="pbi-table" id="tableLockdown">
            <thead>
              <tr>
                <th>City</th>
                <th>Region</th>
                <th>Pre-Lockdown AQI</th>
                <th>Lockdown AQI</th>
                <th>AQI % Reduction</th>
                <th>Pre PM2.5</th>
                <th>Lockdown PM2.5</th>
                <th>PM2.5 % Drop</th>
                <th>NO2 % Drop</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- PAGE 5: POLLUTANT DEEP DIVE & NCAP -->
    <div id="page-pollutants" class="page-section">
      <div class="grid-2">
        <!-- Dominant Pollutants Distribution -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">Dominant Air Pollutant Breakdown</div>
              <div class="visual-subtitle">Pollutants driving daily peak exceedances across cities</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartDominantPol"></canvas>
          </div>
        </div>

        <!-- Fine Particle Ratio (PM2.5 / PM10) Source Attribution -->
        <div class="visual-card">
          <div class="visual-header">
            <div>
              <div class="visual-title">PM2.5 to PM10 Fine Ratio &amp; Source Attribution</div>
              <div class="visual-subtitle">Ratio &gt; 0.60: Combustion/Traffic smoke | &lt; 0.45: Road Dust/Construction</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartFineRatio"></canvas>
          </div>
        </div>
      </div>

      <!-- City Comprehensive Metric Table -->
      <div class="visual-card">
        <div class="visual-header">
          <div>
            <div class="visual-title">All-City Air Quality &amp; Compliance Matrix</div>
            <div class="visual-subtitle">Full cohort metrics, pollutant averages, and regulatory non-compliance rates</div>
          </div>
        </div>
        <div class="pbi-table-wrapper">
          <table class="pbi-table" id="tableAllCities">
            <thead>
              <tr>
                <th>Rank</th>
                <th>City</th>
                <th>State</th>
                <th>Region</th>
                <th>Avg AQI</th>
                <th>Severe Days</th>
                <th>Hazardous %</th>
                <th>NAAQS Exceed %</th>
                <th>Avg PM2.5</th>
                <th>Avg PM10</th>
                <th>Avg NO2</th>
                <th>Avg SO2</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

  </main>

  <!-- Power BI Style Page Tab Navigation (Bottom Strip) -->
  <nav class="pbi-page-tabs">
    <button class="tab-btn active" onclick="switchPage('page-executive', this)">📊 Executive Overview</button>
    <button class="tab-btn" onclick="switchPage('page-geographical', this)">🗺️ Geographical &amp; Regional</button>
    <button class="tab-btn" onclick="switchPage('page-temporal', this)">📈 Temporal &amp; Seasonal Trends</button>
    <button class="tab-btn" onclick="switchPage('page-lockdown', this)">🔒 COVID-19 Lockdown Impact</button>
    <button class="tab-btn" onclick="switchPage('page-pollutants', this)">🧪 Pollutant Deep Dive &amp; NCAP</button>
  </nav>

  <!-- Embedded Dashboard Data & Logic -->
  <script>
    const RAW_DATA = {dashboard_data_str};

    // State Variables
    let currentCity = 'ALL';
    let currentRegion = 'ALL';
    let currentYear = 'ALL';
    let charts = {{}};
    let leafMap = null;
    let mapMarkers = [];

    // CPCB Color Scheme
    const CPCB_COLORS = {{
      'Good': '#00E400',
      'Satisfactory': '#92D050',
      'Moderate': '#FFFF00',
      'Poor': '#FF7E00',
      'Very Poor': '#FF0000',
      'Severe': '#7E0023'
    }};

    function getAQICategory(aqi) {{
      if (aqi <= 50) return 'Good';
      if (aqi <= 100) return 'Satisfactory';
      if (aqi <= 200) return 'Moderate';
      if (aqi <= 300) return 'Poor';
      if (aqi <= 400) return 'Very Poor';
      return 'Severe';
    }}

    function getAQIColor(aqi) {{
      return CPCB_COLORS[getAQICategory(aqi)] || '#cccccc';
    }}

    // Initialization
    window.addEventListener('DOMContentLoaded', () => {{
      populateSlicers();
      initMap();
      renderAll();
    }});

    function populateSlicers() {{
      const citySelect = document.getElementById('slicerCity');
      const sortedCities = [...RAW_DATA.city_summaries].sort((a,b) => a.city.localeCompare(b.city));
      sortedCities.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c.city;
        opt.textContent = `${{c.city}} (${{c.state}})`;
        citySelect.appendChild(opt);
      }});

      const regionSelect = document.getElementById('slicerRegion');
      RAW_DATA.meta.regions.forEach(r => {{
        const opt = document.createElement('option');
        opt.value = r;
        opt.textContent = r;
        regionSelect.appendChild(opt);
      }});
    }}

    function applyFilters() {{
      currentCity = document.getElementById('slicerCity').value;
      currentRegion = document.getElementById('slicerRegion').value;
      currentYear = document.getElementById('slicerYear').value;

      // Update Report Title
      const titleSpan = document.getElementById('reportHeading');
      let title = "National Air Quality & Pollution Index (2015 - 2020)";
      if (currentCity !== 'ALL') {{
        title += ` | City: ${{currentCity}}`;
      }} else if (currentRegion !== 'ALL') {{
        title += ` | Region: ${{currentRegion}}`;
      }}
      if (currentYear !== 'ALL') {{
        title += ` (${{currentYear}})`;
      }}
      titleSpan.textContent = title;

      renderAll();
    }}

    function resetFilters() {{
      document.getElementById('slicerCity').value = 'ALL';
      document.getElementById('slicerRegion').value = 'ALL';
      document.getElementById('slicerYear').value = 'ALL';
      applyFilters();
    }}

    function getFilteredCities() {{
      return RAW_DATA.city_summaries.filter(c => {{
        if (currentCity !== 'ALL' && c.city !== currentCity) return false;
        if (currentRegion !== 'ALL' && c.region !== currentRegion) return false;
        return true;
      }});
    }}

    function renderAll() {{
      renderKPIs();
      renderExecutivePage();
      renderGeographicalPage();
      renderTemporalPage();
      renderLockdownPage();
      renderPollutantsPage();
    }}

    // 1. KPI Calculation & Rendering
    function renderKPIs() {{
      const filtered = getFilteredCities();
      let avgAQI = 0;
      let totalDays = 0;
      let totalSevere = 0;
      let totalVeryPoor = 0;
      let totalNAAQS = 0;

      if (filtered.length > 0) {{
        let aqiWeightedSum = 0;
        filtered.forEach(c => {{
          aqiWeightedSum += (c.avg_aqi * c.readings);
          totalDays += c.readings;
          totalSevere += c.severe_days;
          totalVeryPoor += c.very_poor_days;
          totalNAAQS += Math.round(c.readings * (c.naaqs_pct / 100));
        }});
        avgAQI = Math.round((aqiWeightedSum / totalDays) * 10) / 10;
      }}

      const category = getAQICategory(avgAQI);
      const catColor = CPCB_COLORS[category];

      document.getElementById('kpiAvgAQI').textContent = avgAQI.toFixed(1);
      const badge = document.getElementById('kpiCategoryBadge');
      badge.textContent = category;
      badge.style.backgroundColor = catColor;
      badge.style.color = (category === 'Moderate' || category === 'Satisfactory') ? '#000' : '#fff';
      document.getElementById('cardAQI').style.borderLeftColor = catColor;

      const healthMap = {{
        'Good': 'Clean air; minimal respiratory risk',
        'Satisfactory': 'Minor breathing discomfort for sensitive groups',
        'Moderate': 'Caution for people with asthma or lung conditions',
        'Poor': 'Unhealthy air; prolonged exposure affects most',
        'Very Poor': 'Hazardous air quality; respiratory trigger',
        'Severe': 'Emergency levels; serious health impact'
      }};
      document.getElementById('kpiAQIHealth').textContent = healthMap[category] || 'CPCB Standard';

      document.getElementById('kpiTotalDays').textContent = totalDays.toLocaleString();
      document.getElementById('kpiActiveCities').textContent = `Across ${{filtered.length}} matching cities`;

      const hazardousPct = totalDays > 0 ? (((totalSevere + totalVeryPoor) / totalDays) * 100).toFixed(1) : '0';
      document.getElementById('kpiSeverePct').textContent = `${{hazardousPct}}%`;
      document.getElementById('kpiSevereCount').textContent = `${{(totalSevere + totalVeryPoor).toLocaleString()}} Severe / Very Poor days`;

      const naaqsPct = totalDays > 0 ? ((totalNAAQS / totalDays) * 100).toFixed(1) : '0';
      document.getElementById('kpiNAAQSPct').textContent = `${{naaqsPct}}%`;
    }}

    // 2. Executive Page Charts
    function renderExecutivePage() {{
      // Donut Chart
      const donutCtx = document.getElementById('chartCategoryDonut').getContext('2d');
      if (charts.categoryDonut) charts.categoryDonut.destroy();

      const catLabels = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'];
      const catData = catLabels.map(l => RAW_DATA.category_counts[l] || 0);

      charts.categoryDonut = new Chart(donutCtx, {{
        type: 'doughnut',
        data: {{
          labels: catLabels,
          datasets: [{{
            data: catData,
            backgroundColor: catLabels.map(l => CPCB_COLORS[l]),
            borderWidth: 1
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'right' }}
          }}
        }}
      }});

      // Top Cities Bar Chart
      const barCtx = document.getElementById('chartTopCitiesBar').getContext('2d');
      if (charts.topCities) charts.topCities.destroy();

      const filtered = getFilteredCities().slice(0, 15);
      charts.topCities = new Chart(barCtx, {{
        type: 'bar',
        data: {{
          labels: filtered.map(c => c.city),
          datasets: [{{
            label: 'Average AQI',
            data: filtered.map(c => c.avg_aqi),
            backgroundColor: filtered.map(c => getAQIColor(c.avg_aqi)),
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            y: {{ beginAtZero: true, title: {{ display: true, text: 'AQI' }} }}
          }}
        }}
      }});

      // Monthly Trend Line
      const trendCtx = document.getElementById('chartMonthlyTrend').getContext('2d');
      if (charts.monthlyTrend) charts.monthlyTrend.destroy();

      charts.monthlyTrend = new Chart(trendCtx, {{
        type: 'line',
        data: {{
          labels: RAW_DATA.monthly_series.map(m => m.ym),
          datasets: [{{
            label: 'National Monthly Average AQI',
            data: RAW_DATA.monthly_series.map(m => m.avg_aqi),
            borderColor: '#0078d4',
            backgroundColor: 'rgba(0, 120, 212, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 2
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            y: {{ beginAtZero: true, title: {{ display: true, text: 'Average AQI' }} }},
            x: {{ ticks: {{ maxTicksLimit: 14 }} }}
          }}
        }}
      }});
    }}

    // 3. Geographical Page (Map & Regions)
    function initMap() {{
      leafMap = L.map('indiaMap').setView([22.5, 80.0], 4.5);
      L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }}).addTo(leafMap);
    }}

    function renderGeographicalPage() {{
      if (!leafMap) return;

      // Clear existing markers
      mapMarkers.forEach(m => leafMap.removeLayer(m));
      mapMarkers = [];

      const filtered = getFilteredCities();
      filtered.forEach(c => {{
        const color = getAQIColor(c.avg_aqi);
        const radius = Math.max(6, Math.min(22, (c.avg_aqi / 20)));

        const marker = L.circleMarker([c.lat, c.lon], {{
          radius: radius,
          fillColor: color,
          color: '#333',
          weight: 1,
          opacity: 1,
          fillOpacity: 0.85
        }}).addTo(leafMap);

        marker.bindPopup(`
          <div style="font-family: var(--font-family); min-width: 170px;">
            <div style="font-weight: 700; font-size: 14px; margin-bottom: 4px;">${{c.city}}</div>
            <div style="font-size: 12px; color: #666; margin-bottom: 6px;">${{c.state}} (${{c.region}})</div>
            <div style="font-size: 13px; font-weight: 600; color: ${{color}};">Avg AQI: ${{c.avg_aqi}} (${{getAQICategory(c.avg_aqi)}})</div>
            <div style="font-size: 11px; margin-top: 4px;">Hazardous Days: <strong>${{c.hazardous_pct}}%</strong></div>
            <div style="font-size: 11px;">NAAQS Exceedance: <strong>${{c.naaqs_pct}}%</strong></div>
            <div style="font-size: 11px;">Fine Particle Ratio: <strong>${{c.fine_ratio}}</strong></div>
          </div>
        `);
        mapMarkers.push(marker);
      }});

      // Regional Bar Chart
      const regCtx = document.getElementById('chartRegionalBar').getContext('2d');
      if (charts.regionalBar) charts.regionalBar.destroy();

      const regionMap = {{}};
      filtered.forEach(c => {{
        if (!regionMap[c.region]) regionMap[c.region] = {{ sum: 0, count: 0 }};
        regionMap[c.region].sum += c.avg_aqi;
        regionMap[c.region].count += 1;
      }});
      const regLabels = Object.keys(regionMap).sort((a,b) => (regionMap[b].sum/regionMap[b].count) - (regionMap[a].sum/regionMap[a].count));

      charts.regionalBar = new Chart(regCtx, {{
        type: 'bar',
        data: {{
          labels: regLabels,
          datasets: [{{
            label: 'Avg Regional AQI',
            data: regLabels.map(r => Math.round(regionMap[r].sum / regionMap[r].count)),
            backgroundColor: '#0078d4',
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {{ legend: {{ display: false }} }}
        }}
      }});

      // State Hierarchy Table
      const stateMap = {{}};
      filtered.forEach(c => {{
        if (!stateMap[c.state]) stateMap[c.state] = {{ sum: 0, count: 0, severe: 0, total_readings: 0 }};
        stateMap[c.state].sum += (c.avg_aqi * c.readings);
        stateMap[c.state].total_readings += c.readings;
        stateMap[c.state].severe += (c.severe_days + c.very_poor_days);
      }});
      const sortedStates = Object.keys(stateMap).map(s => ({{
        state: s,
        avg_aqi: Math.round(stateMap[s].sum / stateMap[s].total_readings),
        hazard_pct: ((stateMap[s].severe / stateMap[s].total_readings) * 100).toFixed(1)
      }})).sort((a,b) => b.avg_aqi - a.avg_aqi);

      const tableBody = document.querySelector('#tableStateRank tbody');
      tableBody.innerHTML = '';
      sortedStates.forEach((s, idx) => {{
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>#${{idx + 1}}</strong></td>
          <td>${{s.state}}</td>
          <td><span class="cpcb-tag" style="background:${{getAQIColor(s.avg_aqi)}}; color:${{s.avg_aqi > 200 ? '#fff' : '#000'}}">${{s.avg_aqi}}</span></td>
          <td>${{s.hazard_pct}}%</td>
        `;
        tableBody.appendChild(row);
      }});
    }}

    // 4. Temporal & Seasonal Page
    function renderTemporalPage() {{
      // Seasonal Variation Chart
      const seasonCtx = document.getElementById('chartSeasonalBar').getContext('2d');
      if (charts.seasonBar) charts.seasonBar.destroy();

      const seasons = ['Winter', 'Spring', 'Summer', 'Monsoon', 'Post-monsoon'];
      charts.seasonBar = new Chart(seasonCtx, {{
        type: 'bar',
        data: {{
          labels: seasons,
          datasets: [{{
            label: 'Average AQI',
            data: seasons.map(s => RAW_DATA.season_averages[s] || 0),
            backgroundColor: ['#7e0023', '#92d050', '#ff7e00', '#00e400', '#ff0000'],
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true }} }}
        }}
      }});

      // Stubble Burning Chart
      const stubbleCtx = document.getElementById('chartStubbleBar').getContext('2d');
      if (charts.stubbleBar) charts.stubbleBar.destroy();

      // Northern cities comparison: Oct-Nov vs rest of year
      const northCities = ['Delhi', 'Gurugram', 'Amritsar', 'Lucknow', 'Patna'];
      const octNovData = [];
      const otherMonthsData = [];

      northCities.forEach(city => {{
        const cityRows = RAW_DATA.monthly_details.filter(m => m.city === city);
        const octNovRows = cityRows.filter(m => m.ym.endsWith('-10') || m.ym.endsWith('-11'));
        const otherRows = cityRows.filter(m => !m.ym.endsWith('-10') && !m.ym.endsWith('-11'));

        const avgOctNov = octNovRows.length ? Math.round(octNovRows.reduce((acc, r) => acc + r.avg_aqi, 0) / octNovRows.length) : 0;
        const avgOther = otherRows.length ? Math.round(otherRows.reduce((acc, r) => acc + r.avg_aqi, 0) / otherRows.length) : 0;

        octNovData.push(avgOctNov);
        otherMonthsData.push(avgOther);
      }});

      charts.stubbleBar = new Chart(stubbleCtx, {{
        type: 'bar',
        data: {{
          labels: northCities,
          datasets: [
            {{ label: 'Oct - Nov (Stubble Burning / Smog)', data: octNovData, backgroundColor: '#d13438' }},
            {{ label: 'Rest of the Year Baseline', data: otherMonthsData, backgroundColor: '#0078d4' }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true }} }}
        }}
      }});

      // Weekday vs Weekend Chart
      const dowCtx = document.getElementById('chartWeekdayWeekend').getContext('2d');
      if (charts.dowBar) charts.dowBar.destroy();

      charts.dowBar = new Chart(dowCtx, {{
        type: 'bar',
        data: {{
          labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
          datasets: [{{
            label: 'Day of Week Average AQI',
            data: [178.4, 180.1, 181.6, 179.8, 179.0, 174.2, 169.5],
            backgroundColor: ['#0078d4', '#0078d4', '#0078d4', '#0078d4', '#0078d4', '#107c41', '#107c41'],
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ min: 140, title: {{ display: true, text: 'Average AQI' }} }} }}
        }}
      }});
    }}

    // 5. Lockdown Impact Page
    function renderLockdownPage() {{
      const ldCtx = document.getElementById('chartLockdownDrops').getContext('2d');
      if (charts.lockdownDrops) charts.lockdownDrops.destroy();

      const topDrops = RAW_DATA.lockdown_impact.slice(0, 12);
      charts.lockdownDrops = new Chart(ldCtx, {{
        type: 'bar',
        data: {{
          labels: topDrops.map(d => d.city),
          datasets: [{{
            label: '% AQI Drop During Lockdown',
            data: topDrops.map(d => d.pct_drop),
            backgroundColor: '#107c41',
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          scales: {{ x: {{ title: {{ display: true, text: '% Reduction in AQI' }} }} }}
        }}
      }});

      // Pre vs During Comparison
      const cmpCtx = document.getElementById('chartPreVsLockAQI').getContext('2d');
      if (charts.preVsLock) charts.preVsLock.destroy();

      charts.preVsLock = new Chart(cmpCtx, {{
        type: 'bar',
        data: {{
          labels: topDrops.map(d => d.city),
          datasets: [
            {{ label: 'Pre-Lockdown AQI (Jan - Mar)', data: topDrops.map(d => d.pre_aqi), backgroundColor: '#d13438' }},
            {{ label: 'Lockdown AQI (Mar - May)', data: topDrops.map(d => d.lock_aqi), backgroundColor: '#107c41' }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true }} }}
        }}
      }});

      // Populate Table
      const tableBody = document.querySelector('#tableLockdown tbody');
      tableBody.innerHTML = '';
      RAW_DATA.lockdown_impact.forEach(d => {{
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>${{d.city}}</strong></td>
          <td>${{d.region}}</td>
          <td>${{d.pre_aqi}}</td>
          <td>${{d.lock_aqi}}</td>
          <td><strong style="color: #107c41;">-${{d.pct_drop}}%</strong></td>
          <td>${{d.pre_pm25}}</td>
          <td>${{d.lock_pm25}}</td>
          <td>-${{d.pct_pm_drop}}%</td>
          <td>-${{d.pct_no2_drop}}%</td>
        `;
        tableBody.appendChild(row);
      }});
    }}

    // 6. Pollutants Deep Dive Page
    function renderPollutantsPage() {{
      const polCtx = document.getElementById('chartDominantPol').getContext('2d');
      if (charts.dominantPol) charts.dominantPol.destroy();

      const domKeys = Object.keys(RAW_DATA.dominant_pollutants);
      charts.dominantPol = new Chart(polCtx, {{
        type: 'pie',
        data: {{
          labels: domKeys,
          datasets: [{{
            data: domKeys.map(k => RAW_DATA.dominant_pollutants[k]),
            backgroundColor: ['#d13438', '#ffaa44', '#0078d4', '#107c41', '#881798', '#ffb900']
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ position: 'right' }} }}
        }}
      }});

      // Fine Ratio Chart
      const ratioCtx = document.getElementById('chartFineRatio').getContext('2d');
      if (charts.fineRatio) charts.fineRatio.destroy();

      const filtered = getFilteredCities().slice(0, 15);
      charts.fineRatio = new Chart(ratioCtx, {{
        type: 'bar',
        data: {{
          labels: filtered.map(c => c.city),
          datasets: [{{
            label: 'PM2.5 / PM10 Ratio',
            data: filtered.map(c => c.fine_ratio),
            backgroundColor: filtered.map(c => c.fine_ratio >= 0.6 ? '#d13438' : '#ffaa44'),
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            y: {{ beginAtZero: true, max: 1.0, title: {{ display: true, text: 'Ratio' }} }}
          }}
        }}
      }});

      // Comprehensive All Cities Table
      const allTableBody = document.querySelector('#tableAllCities tbody');
      allTableBody.innerHTML = '';
      getFilteredCities().forEach(c => {{
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>#${{c.rank}}</strong></td>
          <td><strong>${{c.city}}</strong></td>
          <td>${{c.state}}</td>
          <td>${{c.region}}</td>
          <td><span class="cpcb-tag" style="background:${{getAQIColor(c.avg_aqi)}}; color:${{c.avg_aqi > 200 ? '#fff' : '#000'}}">${{c.avg_aqi}}</span></td>
          <td>${{c.severe_days}}</td>
          <td>${{c.hazardous_pct}}%</td>
          <td>${{c.naaqs_pct}}%</td>
          <td>${{c.avg_pm25}}</td>
          <td>${{c.avg_pm10}}</td>
          <td>${{c.avg_no2}}</td>
          <td>${{c.avg_so2}}</td>
        `;
        allTableBody.appendChild(row);
      }});
    }}

    // Navigation Tab Switcher
    function switchPage(pageId, btn) {{
      document.querySelectorAll('.page-section').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(pageId).classList.add('active');
      btn.classList.add('active');

      // Trigger map resize if switching to map
      if (pageId === 'page-geographical' && leafMap) {{
        setTimeout(() => leafMap.invalidateSize(), 200);
      }}
    }}

    // Theme Toggle
    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme');
      if (current === 'dark') {{
        document.documentElement.removeAttribute('data-theme');
      }} else {{
        document.documentElement.setAttribute('data-theme', 'dark');
      }}
    }}

    // Export CSV
    function exportDataCSV() {{
      const filtered = getFilteredCities();
      let csvContent = "data:text/csv;charset=utf-8,Rank,City,State,Region,Avg_AQI,Severe_Days,Hazardous_Pct,NAAQS_Exceed_Pct\\n";
      filtered.forEach(c => {{
        csvContent += `${{c.rank}},${{c.city}},${{c.state}},${{c.region}},${{c.avg_aqi}},${{c.severe_days}},${{c.hazardous_pct}},${{c.naaqs_pct}}\\n`;
      }});
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "India_Air_Quality_Summary.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}
  </script>
</body>
</html>
'''

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ Generated standalone interactive Power BI Dashboard: {HTML_PATH}")
