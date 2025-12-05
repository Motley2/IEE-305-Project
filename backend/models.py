from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Region(SQLModel, table=True):
    __tablename__ = "Region"
    
    region_id: int = Field(primary_key=True)
    region_name: str = Field(nullable=False)
    country: str = Field(nullable=False)
    population: Optional[int] = None
    
    # Relationship
    earthquakes: list["Earthquake"] = Relationship(back_populates="region")


class SeismicZone(SQLModel, table=True):
    __tablename__ = "SeismicZone"
    
    zone_id: int = Field(primary_key=True)
    zone_name: str = Field(nullable=False)
    risk_level: int = Field(nullable=False)
    
    # Relationship
    earthquakes: list["Earthquake"] = Relationship(back_populates="zone")


class Earthquake(SQLModel, table=True):
    __tablename__ = "Earthquake"
    
    quake_id: Optional[int] = Field(default=None, primary_key=True)
    datetime: str = Field(nullable=False)
    magnitude: float = Field(nullable=False)
    depth_km: float = Field(nullable=False)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    place: str = Field(nullable=False)
    region_id: int = Field(foreign_key="Region.region_id", nullable=False)
    zone_id: int = Field(foreign_key="SeismicZone.zone_id", nullable=False)
    
    # Relationships
    region: Region = Relationship(back_populates="earthquakes")
    zone: SeismicZone = Relationship(back_populates="earthquakes")