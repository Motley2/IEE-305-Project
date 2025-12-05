from typing import Any, Dict, List
from sqlmodel import Session, select, func, col
from sqlalchemy import and_, between
from .database import engine
from .models import Earthquake, Region, SeismicZone


def get_quakes_in_region(region_id: int):
    """Get all earthquakes in a specific region."""
    with Session(engine) as session:
        statement = (
            select(
                Earthquake.quake_id,
                Earthquake.datetime,
                Earthquake.magnitude,
                Earthquake.depth_km,
                Earthquake.latitude,
                Earthquake.longitude,
                Earthquake.place,
                Region.region_name
            )
            .select_from(Earthquake)
            .join(Region)
            .where(Region.region_id == region_id)
            .order_by(Earthquake.datetime.desc())
        )
        results = session.exec(statement).all()
        return [
            {
                "quake_id": r[0],
                "datetime": r[1],
                "magnitude": r[2],
                "depth_km": r[3],
                "latitude": r[4],
                "longitude": r[5],
                "place": r[6],
                "region_name": r[7],
            }
            for r in results
        ]


def get_avg_magnitude_in_region(region_id: int):
    """Calculate the average earthquake magnitude for a specific region."""
    with Session(engine) as session:
        statement = (
            select(
                Region.region_id,
                Region.region_name,
                func.avg(Earthquake.magnitude).label("avg_magnitude")
            )
            .select_from(Earthquake)
            .join(Region)
            .where(Region.region_id == region_id)
            .group_by(Region.region_id, Region.region_name)
        )
        results = session.exec(statement).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "avg_magnitude": r[2],
            }
            for r in results
        ]


def count_quakes_near_location(
    lat_center: float,
    lon_center: float,
    lat_delta: float = 1.0,
    lon_delta: float = 1.0,
):
    """Count earthquakes within a bounding box around a given location."""
    lat_min = lat_center - lat_delta
    lat_max = lat_center + lat_delta
    lon_min = lon_center - lon_delta
    lon_max = lon_center + lon_delta

    with Session(engine) as session:
        statement = select(func.count(Earthquake.quake_id).label("quake_count")).where(
            and_(
                between(Earthquake.latitude, lat_min, lat_max),
                between(Earthquake.longitude, lon_min, lon_max)
            )
        )
        result = session.exec(statement).first()
        return [{"quake_count": result}]


def get_most_active_regions(top_n: int = 5):
    """
    Return the top-N regions by earthquake count.
    """
    with Session(engine) as session:
        statement = (
            select(
                Region.region_id,
                Region.region_name,
                Region.country,
                func.count(Earthquake.quake_id).label("quake_count")
            )
            .select_from(Earthquake)
            .join(Region)
            .group_by(Region.region_id, Region.region_name, Region.country)
            .order_by(func.count(Earthquake.quake_id).desc())
            .limit(top_n)
        )
        results = session.exec(statement).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "country": r[2],
                "quake_count": r[3],
            }
            for r in results
        ]


def get_high_magnitude_quakes(
    min_magnitude: float,
    start_date: str,
    end_date: str,
    limit: int = 50,
):
    """Get high-magnitude earthquakes within a specific date range."""
    start_ts = start_date + " 00:00:00"
    end_ts = end_date + " 23:59:59"

    with Session(engine) as session:
        statement = (
            select(
                Earthquake.quake_id,
                Earthquake.datetime,
                Earthquake.magnitude,
                Earthquake.depth_km,
                Earthquake.latitude,
                Earthquake.longitude,
                Earthquake.place
            )
            .where(
                and_(
                    Earthquake.magnitude >= min_magnitude,
                    between(Earthquake.datetime, start_ts, end_ts)
                )
            )
            .order_by(Earthquake.magnitude.desc(), Earthquake.datetime.desc())
            .limit(limit)
        )
        results = session.exec(statement).all()
        return [
            {
                "quake_id": r[0],
                "datetime": r[1],
                "magnitude": r[2],
                "depth_km": r[3],
                "latitude": r[4],
                "longitude": r[5],
                "place": r[6],
            }
            for r in results
        ]

def get_regions_with_min_quakes(min_quakes: int):
    """Get regions that have more than a minimum number of earthquakes."""
    with Session(engine) as session:
        statement = (
            select(
                Region.region_id,
                Region.region_name,
                func.count(Earthquake.quake_id).label("quake_count")
            )
            .select_from(Earthquake)
            .join(Region)
            .group_by(Region.region_id, Region.region_name)
            .having(func.count(Earthquake.quake_id) > min_quakes)
            .order_by(func.count(Earthquake.quake_id).desc())
        )
        results = session.exec(statement).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "quake_count": r[2],
            }
            for r in results
        ]

def get_regions_above_average_quakes():
    """Get regions with earthquake counts above the global average."""
    from sqlalchemy import text
    
    with Session(engine) as session:
        # Using raw SQL for CTE
        sql = text("""
            WITH region_counts AS (
                SELECT
                    region_id,
                    COUNT(*) AS quake_count
                FROM Earthquake
                GROUP BY region_id
            ),
            avg_count AS (
                SELECT AVG(quake_count) AS avg_quakes
                FROM region_counts
            )
            SELECT
                r.region_id,
                r.region_name,
                rc.quake_count,
                a.avg_quakes
            FROM region_counts AS rc
            JOIN avg_count AS a
            JOIN Region AS r ON rc.region_id = r.region_id
            WHERE rc.quake_count > a.avg_quakes
            ORDER BY rc.quake_count DESC;
        """)
        results = session.exec(sql).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "quake_count": r[2],
                "avg_quakes": r[3],
            }
            for r in results
        ]

def get_multi_criteria_quakes(
    min_magnitude: float,
    min_risk_level: int,
    min_population: int,
):
    """Get earthquakes meeting multiple criteria: minimum magnitude, risk level, and population."""
    with Session(engine) as session:
        statement = (
            select(
                Earthquake.quake_id,
                Earthquake.datetime,
                Earthquake.magnitude,
                Earthquake.depth_km,
                Earthquake.latitude,
                Earthquake.longitude,
                Earthquake.place,
                Region.region_name,
                Region.population,
                SeismicZone.zone_name,
                SeismicZone.risk_level
            )
            .select_from(Earthquake)
            .join(Region)
            .join(SeismicZone)
            .where(
                and_(
                    Earthquake.magnitude >= min_magnitude,
                    SeismicZone.risk_level >= min_risk_level,
                    Region.population.is_not(None),
                    Region.population >= min_population
                )
            )
            .order_by(Earthquake.magnitude.desc(), Earthquake.datetime.desc())
        )
        results = session.exec(statement).all()
        return [
            {
                "quake_id": r[0],
                "datetime": r[1],
                "magnitude": r[2],
                "depth_km": r[3],
                "latitude": r[4],
                "longitude": r[5],
                "place": r[6],
                "region_name": r[7],
                "population": r[8],
                "zone_name": r[9],
                "risk_level": r[10],
            }
            for r in results
        ]

def get_quakes_in_high_population_regions(min_population: int):
    """Get earthquake counts for regions with population above a minimum threshold."""
    with Session(engine) as session:
        statement = (
            select(
                Region.region_id,
                Region.region_name,
                Region.population,
                func.count(Earthquake.quake_id).label("quake_count")
            )
            .select_from(Earthquake)
            .join(Region)
            .where(
                and_(
                    Region.population.is_not(None),
                    Region.population >= min_population
                )
            )
            .group_by(Region.region_id, Region.region_name, Region.population)
            .order_by(func.count(Earthquake.quake_id).desc())
        )
        results = session.exec(statement).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "population": r[2],
                "quake_count": r[3],
            }
            for r in results
        ]

def get_region_risk_summary(region_id: int):
    """Get a comprehensive seismic risk summary for a specific region."""
    with Session(engine) as session:
        statement = (
            select(
                Region.region_id,
                Region.region_name,
                Region.country,
                Region.population,
                SeismicZone.zone_id,
                SeismicZone.zone_name,
                SeismicZone.risk_level,
                func.count(Earthquake.quake_id).label("quake_count"),
                func.avg(Earthquake.magnitude).label("avg_magnitude"),
                func.max(Earthquake.magnitude).label("max_magnitude")
            )
            .select_from(Region)
            .join(Earthquake)
            .join(SeismicZone)
            .where(Region.region_id == region_id)
            .group_by(
                Region.region_id,
                Region.region_name,
                Region.country,
                Region.population,
                SeismicZone.zone_id,
                SeismicZone.zone_name,
                SeismicZone.risk_level
            )
        )
        results = session.exec(statement).all()
        return [
            {
                "region_id": r[0],
                "region_name": r[1],
                "country": r[2],
                "population": r[3],
                "zone_id": r[4],
                "zone_name": r[5],
                "risk_level": r[6],
                "quake_count": r[7],
                "avg_magnitude": r[8],
                "max_magnitude": r[9],
            }
            for r in results
        ]