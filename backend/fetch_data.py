import requests
from datetime import datetime, timezone
from sqlmodel import Session

from .database import engine, init_db
from .models import Region, SeismicZone, Earthquake


BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# filter window parameters
params = {
    "format": "geojson",
    "starttime": "2025-01-01",
    "endtime": today,
    "minmagnitude": 3,
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

    # 9. Caribbean Arc (Puerto Rico / USVI)
    if 15.0 <= lat <= 22.0 and -72.0 <= lon <= -60.0:
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

    # 9 = Caribbean Subduction Zone (Puerto Rico Trench)
    if 15.0 <= lat <= 22.0 and -70.0 <= lon <= -60.0:
        return 9
    
    # 10 = Other Oceanic / Miscellaneous
    return 10




def seed_lookup_tables(session: Session):
    # Seed Region table
    regions = [
        Region(region_id=1, region_name="California Margin", country="USA", population=39_200_000),
        Region(region_id=2, region_name="Alaska/Aleutian Margin", country="USA", population=733_000),
        Region(region_id=3, region_name="NW Pacific Margin (Japan/Russia)", country="Japan + Russian Far East", population=125_700_000 + 6_300_000),
        Region(region_id=4, region_name="Chile Subduction Zone", country="Chile", population=19_600_000),
        Region(region_id=5, region_name="Indonesia/Philippines/PNG Arc", country="Indonesia + Philippines + PNG", population=277_500_000 + 117_300_000 + 9_700_000),
        Region(region_id=6, region_name="New Zealand & SW Pacific", country="NZ + Fiji + Tonga + Samoa", population=5_200_000 + 940_000 + 107_000 + 225_000),
        Region(region_id=7, region_name="Mediterranean Region", country="Turkey + Greece + Italy + Balkans", population=85_000_000 + 10_300_000 + 58_900_000 + 18_000_000),
        Region(region_id=8, region_name="Himalaya/Central Asia Belt", country="India North + Nepal + Pakistan North + China West", population=600_000_000 + 30_300_000 + 70_000_000 + 95_000_000),
        Region(region_id=9, region_name="Caribbean Arc (Puerto Rico / USVI)", country="Multiple", population=12_000_000),
        Region(region_id=10, region_name="Other", country="Various", population=None),
    ]
    
    for region in regions:
        # Use merge to handle INSERT OR IGNORE behavior
        session.merge(region)
    
    # Seed SeismicZone table
    zones = [
        SeismicZone(zone_id=1, zone_name='US Pacific Subduction Margin', risk_level=5),
        SeismicZone(zone_id=2, zone_name='Japan Trench Zone', risk_level=5),
        SeismicZone(zone_id=3, zone_name='Andean Subduction Zone', risk_level=5),
        SeismicZone(zone_id=4, zone_name='Sunda Arc (Indonesia)', risk_level=5),
        SeismicZone(zone_id=5, zone_name='New Zealand Plate Boundary', risk_level=4),
        SeismicZone(zone_id=6, zone_name='Mediterranean Collision/Subduction', risk_level=4),
        SeismicZone(zone_id=7, zone_name='Himalayan Collision Belt', risk_level=4),
        SeismicZone(zone_id=8, zone_name='Mid-Atlantic Ridge', risk_level=3),
        SeismicZone(zone_id=9, zone_name='Caribbean Subduction Zone (Puerto Rico Trench)', risk_level=4),
        SeismicZone(zone_id=10, zone_name='Other Oceanic Zone', risk_level=2),
    ]
    
    for zone in zones:
        session.merge(zone)
    
    session.commit()




def fetch_and_load():
    # Initialize database and create tables if needed
    init_db()
    
    with Session(engine) as session:
        seed_lookup_tables(session)

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

            earthquake = Earthquake(
                datetime=dt_str,
                magnitude=float(mag),
                depth_km=float(depth_km),
                latitude=float(lat),
                longitude=float(lon),
                place=place_clean,
                region_id=region_id,
                zone_id=zone_id,
            )
            session.add(earthquake)

        session.commit()
    
    print("Finished loading data into earthquakes.db")


if __name__ == "__main__":
    fetch_and_load()
