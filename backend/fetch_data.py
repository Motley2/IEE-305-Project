import requests
from datetime import datetime, timezone

from database import get_connection


BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# filter window parameters
params = {
    "format": "geojson",
    "starttime": "2025-01-01",
    "endtime": today,
    "minmagnitude": 4.5,
    "orderby": "time",
    "limit": 50,
}


# classifiers for region_id and zone_id 

def classify_region(lat: float, lon: float) -> int:
    """
    Return region_id based on rough location.

    1 = California (roughly US West Coast)
    2 = Alaska
    3 = Japan
    4 = Other
    """

    # California-ish
    if 30 <= lat <= 42 and -125 <= lon <= -114:
        return 1

    # Alaska-ish
    if 50 <= lat <= 72 and -170 <= lon <= -130:
        return 2

    # Japan-ish
    if 25 <= lat <= 46 and 128 <= lon <= 147:
        return 3

    # Everything else
    return 4


def classify_zone(lat: float, lon: float) -> int:
    """
    Return zone_id based on plate-margin-ish geography.

    1 = Pacific Plate Margin (US West Coast)
    2 = North American Plate Interior / Alaska
    3 = Japan Trench Zone
    4 = Other
    """

    # Pacific Plate margin near US West Coast
    if 30 <= lat <= 45 and -130 <= lon <= -110:
        return 1

    # North American interior / Alaska region
    if 45 <= lat <= 75 and -170 <= lon <= -60:
        return 2

    # Japan trench
    if 25 <= lat <= 45 and 128 <= lon <= 150:
        return 3

    # Everything else
    return 4




def seed_lookup_tables(conn):
    cur = conn.cursor()

    
    cur.executemany(
        """
        INSERT OR IGNORE INTO Region (region_id, region_name, country, population)
        VALUES (?, ?, ?, ?)
        """,
        [
            (1, "California", "USA", 39_000_000),
            (2, "Alaska", "USA", 731_000),
            (3, "Japan", "Japan", 125_000_000),
            (4, "Other", "Various", None),
        ],
    )

   
    cur.executemany(
        """
        INSERT OR IGNORE INTO SeismicZone (zone_id, zone_name, risk_level)
        VALUES (?, ?, ?)
        """,
        [
            (1, "Pacific Plate Margin", 5),
            (2, "North American Plate", 3),
            (3, "Japan Trench Zone", 5),
            (4, "Other", 2),
        ],
    )

    conn.commit()




def fetch_and_load():
    conn = get_connection()
    seed_lookup_tables(conn)
    cur = conn.cursor()

    print("Requesting data from USGS...")
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    features = data.get("features", [])
    print(f"Fetched {len(features)} earthquakes from USGS")

    

    for feature in features:
        props = feature.get("properties", {}) or {}
        geom = feature.get("geometry", {}) or {}

        coords = geom.get("coordinates", None)
        if coords is None or len(coords) < 3:
            continue

        lon = coords[0]
        lat = coords[1]
        depth_km = coords[2]

        mag = props.get("mag")
        time_ms = props.get("time")
        place_text = props.get("place") or "Unknown location"

        
        if mag is None or time_ms is None or lat is None or lon is None:
            continue

        
        dt = datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc)
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        
        place_clean = place_text.replace(",", " - ")

        region_id = classify_region(lat, lon)
        zone_id = classify_zone(lat, lon)

        cur.execute(
            """
            INSERT INTO Earthquake (
                datetime, magnitude, depth_km,
                latitude, longitude, place, region_id, zone_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dt_str,
                float(mag),
                float(depth_km),
                float(lat),
                float(lon),
                place_clean,
                region_id,
                zone_id,
            ),
        )


    conn.commit()
    conn.close()
    print("Finished loading data into earthquakes.db")


if __name__ == "__main__":
    fetch_and_load()
