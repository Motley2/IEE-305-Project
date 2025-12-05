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
    Map latitude/longitude to a coarse geographic region_id.
    Uses real-world bounding boxes based on country/region extents.
    """

    # Normalize longitude to [-180, 180]
    if lon > 180:
        lon -= 360

    # 1. California
    if 30 <= lat <= 42 and -130 <= lon <= -110:
        return 1

    # 2. Alaska (incl. Aleutians)
    if 50 <= lat <= 72 and -180 <= lon <= -130:
        return 2

    # 3. Japan + Kuril + Kamchatka + Russian Pacific margin
    #    Covers Honshu through far-east Russia along the trench.
    if 30 <= lat <= 65 and 135 <= lon <= 170:
        return 3

    # 4. Chile
    if -60 <= lat <= -15 and -80 <= lon <= -65:
        return 4

    # 5. Indonesia / Philippines / PNG
    if -15 <= lat <= 15 and 95 <= lon <= 155:
        return 5

    # 6. New Zealand + SW Pacific (Fiji / Tonga / Kermadec)
    if -60 <= lat <= -10 and (155 <= lon <= 180 or -180 <= lon <= -160):
        return 6

    # 7. Mediterranean
    if 30 <= lat <= 46 and -10 <= lon <= 40:
        return 7

    # 8. Himalayas / central Asia collision belt (incl. much of China)
    if 20 <= lat <= 45 and 60 <= lon <= 115:
        return 8

    # 9. Mid-Atlantic Ridge (North)
    if -40 <= lat <= 70 and -50 <= lon <= -10:
        return 9

    # 10. Everything else
    return 10


def classify_zone(lat: float, lon: float) -> int:
    """
    Map latitude/longitude to a tectonic seismic zone_id.
    Zones are bigger belts (subduction margins, ridges, collision zones).
    """

    # 1 = US Pacific Subduction Margin (California + Alaska coast)
    if 30.0 <= lat <= 72.5 and -150.0 <= lon <= -110.0:
        return 1

    # 2 = Japan Trench Zone
    if 30.0 <= lat <= 50.0 and 130.0 <= lon <= 160.0:
        return 2

    # 3 = Andean Subduction (Chile–Peru)
    if -60.0 <= lat <= 5.0 and -90.0 <= lon <= -60.0:
        return 3

    # 4 = Sunda Arc (Indonesia)
    if -15.0 <= lat <= 10.0 and 90.0 <= lon <= 150.0:
        return 4

    # 5 = New Zealand Plate Boundary
    if -50.0 <= lat <= -30.0 and 160.0 <= lon <= 180.0:
        return 5

    # 6 = Mediterranean Collision/Subduction
    if 25.0 <= lat <= 50.0 and -10.0 <= lon <= 40.0:
        return 6

    # 7 = Himalayan Collision Belt
    if 20.0 <= lat <= 40.0 and 70.0 <= lon <= 100.0:
        return 7

    # 8 = Mid-Atlantic Ridge
    if -60.0 <= lat <= 60.0 and -40.0 <= lon <= -10.0:
        return 8

    # 9 = Kuril–Kamchatka Subduction Zone
    # Rough box: 45–60°N, 145–175°E (Pacific margin of Kamchatka & Kuril Islands)
    if 45.0 <= lat <= 60.0 and 145.0 <= lon <= 175.0:
      return 9
    
    # 10 = Other Oceanic / Miscellaneous
    return 10




def seed_lookup_tables(conn):
    cur = conn.cursor()

    
    cur.executemany(
    """
    INSERT OR IGNORE INTO Region (region_id, region_name, country, population)
    VALUES (?, ?, ?, ?)
    """,
    [
        # 1. California
        (1,  "California Margin",                 
             "USA", 
             39_200_000),

        # 2. Alaska (incl. Aleutians)
        (2,  "Alaska–Aleutian Margin",           
             "USA", 
             733_000),

        # 3. NW Pacific Margin (Japan / Russia Far East / Kuril / Kamchatka)
        (3,  "NW Pacific Margin (Japan/Russia)", 
             "Japan + Russian Far East", 
             125_700_000 + 6_300_000),  # Japan + Russian Far East
             
        # 4. Chile Subduction Zone
        (4,  "Chile Subduction Zone",             
             "Chile", 
             19_600_000),

        # 5. Indonesia / Philippines / PNG Arc
        (5,  "Indonesia–Philippines–PNG Arc",     
             "Indonesia + Philippines + PNG", 
             277_500_000 + 117_300_000 + 9_700_000),

        # 6. New Zealand & SW Pacific (Fiji, Tonga, Kermadec region)
        (6,  "New Zealand & SW Pacific",          
             "NZ + Fiji + Tonga + Samoa", 
             5_200_000 + 940_000 + 107_000 + 225_000),

        # 7. Mediterranean Region
        (7,  "Mediterranean Region",              
             "Turkey + Greece + Italy + Balkans", 
             85_000_000 + 10_300_000 + 58_900_000 + 18_000_000),

        # 8. Himalaya–Central Asia Belt
        (8,  "Himalaya–Central Asia Belt",        
             "India North + Nepal + Pakistan North + China West", 
             600_000_000 + 30_300_000 + 70_000_000 + 95_000_000),

        # 9. North Mid-Atlantic Ridge (oceanic)
        (9,  "North Mid-Atlantic Ridge",          
             "Oceanic", 
             None),  # no resident population

        # 10. Everything else
        (10, "Other",                             
              "Various", 
              None),
    ],
)

   
    cur.executemany(
        """
        INSERT OR IGNORE INTO SeismicZone (zone_id, zone_name, risk_level)
        VALUES (?, ?, ?)
        """,
        [
            (1, 'US Pacific Subduction Margin', 5),
            (2, 'Japan Trench Zone', 5),
            (3, 'Andean Subduction Zone', 5),
            (4, 'Sunda Arc (Indonesia)', 5),
            (5, 'New Zealand Plate Boundary', 4),
            (6, 'Mediterranean Collision/Subduction', 4),
            (7, 'Himalayan Collision Belt', 4),
            (8, 'Mid-Atlantic Ridge', 3),
            (9, 'Kuril–Kamchatka Subduction Zone', 5),
            (10, 'Other Oceanic Zone', 2),
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
