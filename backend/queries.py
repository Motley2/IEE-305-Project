from typing import Any, Dict, List
from database import get_connection


def _rows_to_dicts(cursor, rows) -> List[Dict[str, Any]]:
    """Convert sqlite3 rows to list[dict] using column names."""
    col_names = [desc[0] for desc in cursor.description]
    return [dict(zip(col_names, row)) for row in rows]

def get_quakes_in_region(region_id: int):
    sql = """
        SELECT
            e.quake_id,
            e.datetime,
            e.magnitude,
            e.depth_km,
            e.latitude,
            e.longitude,
            e.place,
            r.region_name
        FROM Earthquake AS e
        JOIN Region AS r ON e.region_id = r.region_id
        WHERE r.region_id = ?
        ORDER BY e.datetime DESC;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (region_id,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_avg_magnitude_in_region(region_id: int):
    sql = """
        SELECT
            r.region_id,
            r.region_name,
            AVG(e.magnitude) AS avg_magnitude
        FROM Earthquake AS e
        JOIN Region AS r ON e.region_id = r.region_id
        WHERE r.region_id = ?
        GROUP BY r.region_id, r.region_name;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (region_id,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def count_quakes_near_location(
    lat_center: float,
    lon_center: float,
    lat_delta: float = 1.0,
    lon_delta: float = 1.0,
):
    sql = """
        SELECT
            COUNT(*) AS quake_count
        FROM Earthquake
        WHERE latitude  BETWEEN ? AND ?
          AND longitude BETWEEN ? AND ?;
    """
    lat_min = lat_center - lat_delta
    lat_max = lat_center + lat_delta
    lon_min = lon_center - lon_delta
    lon_max = lon_center + lon_delta

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (lat_min, lat_max, lon_min, lon_max))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_most_active_regions(top_n: int = 5):
    """
    Return the top-N regions by earthquake count.
    """
    sql = """
        SELECT
            r.region_id,
            r.region_name,
            r.country,
            COUNT(e.quake_id) AS quake_count
        FROM Earthquake AS e
        JOIN Region AS r ON e.region_id = r.region_id
        GROUP BY r.region_id, r.region_name, r.country
        ORDER BY quake_count DESC
        LIMIT ?;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (top_n,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_high_magnitude_quakes(
    min_magnitude: float,
    start_date: str,
    end_date: str,
    limit: int = 50,
):
    """
    Return earthquakes with magnitude >= min_magnitude
    between start_date and end_date (inclusive).
    Dates are strings 'YYYY-MM-DD'.
    """
    start_ts = start_date + " 00:00:00"
    end_ts = end_date + " 23:59:59"

    sql = """
        SELECT
            quake_id,
            datetime,
            magnitude,
            depth_km,
            latitude,
            longitude,
            place
        FROM Earthquake
        WHERE magnitude >= ?
          AND datetime BETWEEN ? AND ?
        ORDER BY magnitude DESC, datetime DESC
        LIMIT ?;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (min_magnitude, start_ts, end_ts, limit))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_regions_with_min_quakes(min_quakes: int):
    """
    Return regions that have more than min_quakes earthquakes.
    """
    sql = """
        SELECT
            r.region_id,
            r.region_name,
            COUNT(e.quake_id) AS quake_count
        FROM Earthquake AS e
        JOIN Region AS r ON e.region_id = r.region_id
        GROUP BY r.region_id, r.region_name
        HAVING COUNT(e.quake_id) > ?
        ORDER BY quake_count DESC;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (min_quakes,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_regions_above_average_quakes():
    """
    Return regions whose quake counts are above the global average.
    Demonstrates a CTE + aggregation.
    """
    sql = """
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
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_multi_criteria_quakes(
    min_magnitude: float,
    min_risk_level: int,
    min_population: int,
):
    """
    Return earthquakes where:
      - magnitude >= min_magnitude
      - zone risk_level >= min_risk_level
      - region population >= min_population
    Uses a 3-table JOIN (Earthquake, Region, SeismicZone).
    """
    sql = """
        SELECT
            e.quake_id,
            e.datetime,
            e.magnitude,
            e.depth_km,
            e.latitude,
            e.longitude,
            e.place,
            r.region_name,
            r.population,
            s.zone_name,
            s.risk_level
        FROM Earthquake AS e
        JOIN Region      AS r ON e.region_id = r.region_id
        JOIN SeismicZone AS s ON e.zone_id   = s.zone_id
        WHERE e.magnitude  >= ?
          AND s.risk_level >= ?
          AND r.population IS NOT NULL
          AND r.population >= ?
        ORDER BY e.magnitude DESC, e.datetime DESC;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (min_magnitude, min_risk_level, min_population))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_quakes_in_high_population_regions(min_population: int):
    """
    Return quake counts for regions with population >= min_population.
    """
    sql = """
        SELECT
            r.region_id,
            r.region_name,
            r.population,
            COUNT(e.quake_id) AS quake_count
        FROM Earthquake AS e
        JOIN Region AS r ON e.region_id = r.region_id
        WHERE r.population IS NOT NULL
          AND r.population >= ?
        GROUP BY r.region_id, r.region_name, r.population
        ORDER BY quake_count DESC;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (min_population,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result

def get_region_risk_summary(region_id: int):
    """
    Summarize seismic risk for a given region:
      - population
      - zone risk_level
      - quake_count
      - avg & max magnitude
    """
    sql = """
        SELECT
            r.region_id,
            r.region_name,
            r.country,
            r.population,
            s.zone_id,
            s.zone_name,
            s.risk_level,
            COUNT(e.quake_id) AS quake_count,
            AVG(e.magnitude)  AS avg_magnitude,
            MAX(e.magnitude)  AS max_magnitude
        FROM Region      AS r
        JOIN Earthquake  AS e ON e.region_id = r.region_id
        JOIN SeismicZone AS s ON e.zone_id   = s.zone_id
        WHERE r.region_id = ?
        GROUP BY
            r.region_id,
            r.region_name,
            r.country,
            r.population,
            s.zone_id,
            s.zone_name,
            s.risk_level;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (region_id,))
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    conn.close()
    return result