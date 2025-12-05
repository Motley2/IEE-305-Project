from typing import Optional
from sqlmodel import SQLModel


class EarthquakeInRegion(SQLModel):
    """Single earthquake row with region name, used for /regions/{id}/earthquakes."""
    quake_id: int
    datetime: str
    magnitude: float
    depth_km: float
    latitude: float
    longitude: float
    place: str
    region_name: str


class AvgMagnitudeResponse(SQLModel):
    """Average magnitude statistics for a region."""
    region_id: int
    region_name: str
    avg_magnitude: float


class NearbyCountResponse(SQLModel):
    """Count of earthquakes near a given location."""
    quake_count: int


class RegionRiskSummary(SQLModel):
    """Risk summary for a region, based on its zone and historical quakes."""
    region_id: int
    region_name: str
    zone_name: str
    risk_level: int
    total_quakes: int
    avg_magnitude: Optional[float]
    max_magnitude: Optional[float]