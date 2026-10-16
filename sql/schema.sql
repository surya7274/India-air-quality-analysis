-- schema.sql
-- PostgreSQL schema for India air quality analysis

CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    state TEXT
);

CREATE TABLE IF NOT EXISTS stations (
    station_id TEXT PRIMARY KEY,
    name TEXT,
    city TEXT REFERENCES cities(name),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS daily_readings (
    reading_id SERIAL PRIMARY KEY,
    city TEXT REFERENCES cities(name),
    station_id TEXT REFERENCES stations(station_id),
    date DATE NOT NULL,
    pm25 DOUBLE PRECISION,
    pm10 DOUBLE PRECISION,
    no DOUBLE PRECISION,
    no2 DOUBLE PRECISION,
    nox DOUBLE PRECISION,
    nh3 DOUBLE PRECISION,
    co DOUBLE PRECISION,
    so2 DOUBLE PRECISION,
    o3 DOUBLE PRECISION,
    benzene DOUBLE PRECISION,
    toluene DOUBLE PRECISION,
    xylene DOUBLE PRECISION,
    aqi INTEGER,
    aqi_bucket INTEGER,
    year INTEGER,
    month INTEGER,
    season TEXT,
    is_weekend BOOLEAN,
    naaqs_exceed BOOLEAN,
    who_exceed BOOLEAN,
    rolling_7day_aqi DOUBLE PRECISION,
    rolling_30day_aqi DOUBLE PRECISION,
    lockdown_flag BOOLEAN,
    city_rank INTEGER,
    dominant_pollutant TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_daily_readings_city_date ON daily_readings (city, date);
CREATE INDEX IF NOT EXISTS idx_daily_readings_aqi ON daily_readings (aqi);
CREATE INDEX IF NOT EXISTS idx_daily_readings_season ON daily_readings (season);
