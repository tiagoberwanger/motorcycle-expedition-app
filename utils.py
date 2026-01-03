import polyline

from haversine import haversine
from typing import List, Tuple


def decode_route_points(encoded_polyline: str) -> List[Tuple[float, float]]:
    """Transforma a string comprimida do Google em lista de coordenadas."""
    return polyline.decode(encoded_polyline)

def calculate_distance(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """Cálculo de Haversine puro entre dois pontos."""
    return haversine(point_a, point_b)
