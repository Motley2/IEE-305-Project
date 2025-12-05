from fastapi import FastAPI, Query
from .queries import (
    get_quakes_in_region,
    get_avg_magnitude_in_region,
    count_quakes_near_location,
    get_most_active_regions,
    get_high_magnitude_quakes,
    get_regions_with_min_quakes,
    get_regions_above_average_quakes,
    get_multi_criteria_quakes,
    get_quakes_in_high_population_regions,
    get_region_risk_summary,
)


app = FastAPI(
    title="Earthquake Analytics API",
    description="Backend for IEE 305 Term Project",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Earthquake Analytics API is running."}


# -----------------------
# Query 1 – Quakes in region
# -----------------------
@app.get("/regions/{region_id}/earthquakes")
def api_quakes_in_region(region_id: int):
    """
    Return all earthquakes for a given region.
    """
    return get_quakes_in_region(region_id)


# -----------------------
# Query 2 – Average magnitude in region
# -----------------------
@app.get("/regions/{region_id}/stats/avg-magnitude")
def api_avg_magnitude(region_id: int):
    """
    Return average magnitude for earthquakes in a region.
    """
    return get_avg_magnitude_in_region(region_id)


# -----------------------
# Query 3 – Quakes near a location
# -----------------------
@app.get("/analytics/nearby")
def api_quakes_nearby(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    lat_delta: float = Query(1.0, description="Latitude ± window"),
    lon_delta: float = Query(1.0, description="Longitude ± window"),
):
    """
    Count earthquakes within a bounding box around a given location.
    """
    return count_quakes_near_location(lat, lon, lat_delta, lon_delta)

# -----------------------
# Query 4 – Most active regions
# -----------------------
@app.get("/analytics/regions/most-active")
def api_most_active_regions(
    top_n: int = Query(5, ge=1, le=50, description="Number of regions to return"),
):
    """
    Return the top-N most active regions by earthquake count.
    """
    return get_most_active_regions(top_n)

# -----------------------
# Query 5 – High magnitude earthquakes
# -----------------------
@app.get("/analytics/high-magnitude")
def api_high_magnitude_quakes(
    min_magnitude: float = Query(6.0, description="Minimum magnitude to include"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=500, description="Max number of records"),
):
    """
    Return high-magnitude earthquakes in a given date range.
    """
    return get_high_magnitude_quakes(min_magnitude, start_date, end_date, limit)

# -----------------------
# Query 6 – Regions with minimum quakes
# -----------------------
@app.get("/analytics/regions/with-min-quakes")
def api_regions_with_min_quakes(
    min_quakes: int = Query(10, ge=1, description="Minimum number of quakes"),
):
    """
    Return regions that have more than min_quakes earthquakes.
    """
    return get_regions_with_min_quakes(min_quakes)

# -----------------------
# Query 7 – Regions above average activity
# -----------------------
@app.get("/analytics/regions/above-average-activity")
def api_regions_above_average():
    """
    Return regions whose quake counts are above the global average.
    """
    return get_regions_above_average_quakes()

# -----------------------
# Query 8 – Multi-criteria earthquakes
# -----------------------
@app.get("/analytics/multi-criteria")
def api_multi_criteria_quakes(
    min_magnitude: float = Query(5.5, description="Minimum magnitude"),
    min_risk_level: int = Query(4, ge=1, le=5, description="Minimum risk level"),
    min_population: int = Query(10_000_000, description="Minimum region population"),
):
    """
    Return earthquakes that satisfy multi-table criteria:
      - magnitude >= min_magnitude
      - zone risk_level >= min_risk_level
      - region population >= min_population
    """
    return get_multi_criteria_quakes(min_magnitude, min_risk_level, min_population)

# -----------------------
# Query 9 – High population regions
# -----------------------
@app.get("/analytics/high-population-regions")
def api_high_population_regions(
    min_population: int = Query(10_000_000, description="Minimum region population"),
):
    """
    Return quake counts for regions with population >= min_population.
    """
    return get_quakes_in_high_population_regions(min_population)

# -----------------------
# Query 10 – Region risk summary
# -----------------------
@app.get("/regions/{region_id}/risk-summary")
def api_region_risk_summary(region_id: int):
    """
    Return a seismic risk summary for a specific region:
      - population
      - zone risk_level
      - quake_count
      - average and max magnitude
    """
    return get_region_risk_summary(region_id)