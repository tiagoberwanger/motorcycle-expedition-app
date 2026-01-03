import polyline

from haversine import haversine
from typing import List, Tuple

from schemas import TimelineEvent


def decode_route_points(encoded_polyline: str) -> List[Tuple[float, float]]:
    """Transforma a string comprimida do Google em lista de coordenadas."""
    return polyline.decode(encoded_polyline)

def calculate_distance(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """Cálculo de Haversine puro entre dois pontos."""
    return haversine(point_a, point_b)

def generate_google_maps_url(origin: str, destination: str, timeline: List[TimelineEvent]) -> str:
    """Gera a url dinâmica do google maps com origem/destino/waypoints."""
    
    maps_url = "https://www.google.com/maps/dir/?api=1"
    all_stops = [f"{t.data.coordinates['lat']},{t.data.coordinates['lng']}" for t in timeline if t.type == "STOP"]
    origin = origin.replace(" ", "")
    destination = destination.replace(" ", "")
    waypoints = "|".join(all_stops)

    return f"{maps_url}&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=motorcycle"
