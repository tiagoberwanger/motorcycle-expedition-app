from typing import List, Union

from pydantic import BaseModel


class Motorcycle(BaseModel):
    fuel_autonomy: float
    fuel_safety_margin: float


class RouteWarning(BaseModel):
    message: str
    coordinates: dict


class RouteStops(BaseModel):
    name: str
    address: str
    coordinates: dict


class TimelineEvent(BaseModel):
    type: str  # "STOP" ou "WARNING"
    start_km: float
    end_km: float
    data: Union[RouteStops, RouteWarning]


class RouteRequest(BaseModel):
    origin: str
    destination: str
    motorcycle: Motorcycle


class RouteResponse(BaseModel):
    total_distance_km: float
    google_maps_url: str
    timeline: List[TimelineEvent]
