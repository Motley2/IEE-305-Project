from typing import List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

from .schemas import (
    EarthquakeInRegion,
    AvgMagnitudeResponse,
    NearbyCountResponse,
    RegionRiskSummary,
)


app = FastAPI(
    title="Earthquake Analytics API",
    description="Backend for IEE 305 Term Project",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Earthquake Analytics API is running."}


# -----------------------
# Query 1 – Quakes in region
# -----------------------
@app.get(
    "/regions/{region_id}/earthquakes",
    response_model=List[EarthquakeInRegion],
    tags=["Regions"],
)
def api_quakes_in_region(region_id: int):
    """
    Returns all earthquakes for a given region.
    Uses a typed response model (EarthquakeInRegion) and returns 404 if there
    are no earthquakes for the given region.
    """
    data = get_quakes_in_region(region_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No earthquakes found for region_id={region_id}.",
        )

    return data


# -----------------------
# Query 2 – Average magnitude in region
# -----------------------
@app.get(
    "/regions/{region_id}/stats/avg-magnitude",
    response_model=AvgMagnitudeResponse,
    tags=["Regions"],
)
def api_avg_magnitude(region_id: int):
    """
    Returns average magnitude for earthquakes in a region.
    Returns 404 if the region has no earthquakes.
    """
    results = get_avg_magnitude_in_region(region_id)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No earthquakes found to compute average for region_id={region_id}.",
        )

    result = get_avg_magnitude_in_region(region_id)
    if result is None:
        ...
    return result


# -----------------------
# Query 3 – Quakes near a location
# -----------------------
@app.get(
    "/analytics/nearby",
    response_model=NearbyCountResponse,
    tags=["Analytics"],
)
def api_quakes_near_location(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    radius_km: float = Query(..., ge=0, description="Search radius in kilometers."),
):
    """
    Count earthquakes within a bounding box around the given lat/lon.
    """
    results = count_quakes_near_location(lat, lon, radius_km)

    # Expecting a list with a single dict like {"quake_count": <int>}
    if not results:
        return {"quake_count": 0}

    return results[0]

# -----------------------
# Query 4 – Most active regions
# -----------------------
@app.get("/analytics/regions/most-active")
def api_most_active_regions(
    top_n: int = Query(5, ge=1, le=10, description="Number of regions to return"),
):
    """
    Return the top-N most active regions by earthquake count.
    Maximum of 10 regions available.
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
@app.get(
    "/regions/{region_id}/risk-summary",
    response_model=RegionRiskSummary,
    tags=["Regions", "Analytics"],
)
def api_region_risk_summary(region_id: int):
    """
    Return risk summary for a specific region, combining:
    - Region info
    - Seismic zone info
    - Aggregated earthquake stats
    """
    results = get_region_risk_summary(region_id)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No risk summary available for region_id={region_id}.",
        )

    return results[0]