PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Earthquake;
DROP TABLE IF EXISTS SeismicZone;
DROP TABLE IF EXISTS Region;

-- 1. Region table
CREATE TABLE Region (
    region_id   INTEGER PRIMARY KEY,
    region_name TEXT    NOT NULL,
    country     TEXT    NOT NULL,
    population  INTEGER         -- may be NULL for 'Other'
);

-- 2. SeismicZone table
CREATE TABLE SeismicZone (
    zone_id   INTEGER PRIMARY KEY,
    zone_name TEXT    NOT NULL,
    risk_level INTEGER NOT NULL
);

-- 3. Earthquake table
CREATE TABLE Earthquake (
    quake_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime   TEXT    NOT NULL,  -- stored as 'YYYY-MM-DD HH:MM:SS' UTC
    magnitude  REAL    NOT NULL,
    depth_km   REAL    NOT NULL,
    latitude   REAL    NOT NULL,
    longitude  REAL    NOT NULL,
    place      TEXT    NOT NULL,  -- USGS "properties.place" (cleaned)
    region_id  INTEGER NOT NULL,
    zone_id    INTEGER NOT NULL,
    FOREIGN KEY (region_id) REFERENCES Region(region_id),
    FOREIGN KEY (zone_id)   REFERENCES SeismicZone(zone_id)
);