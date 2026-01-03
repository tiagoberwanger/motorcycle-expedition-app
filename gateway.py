import httpx

import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class GoogleMapsGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.places_url = "https://places.googleapis.com/v1/places:searchNearby"
        self.routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        self.client = httpx.AsyncClient(timeout=15.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))

    async def close(self):
        await self.client.aclose()

    async def get_motorcycle_route(self, origin: str, destination: str) -> Optional[Dict]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline"
        }

        payload = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": "TWO_WHEELER",
            "routingPreference": "TRAFFIC_UNAWARE"
        }

        try:
            response = await self.client.post(self.routes_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['routes'][0] if data.get('routes') else None

        except Exception as e:
            logger.error(f"Erro ao buscar rota: {e}")
            return None

    async def find_nearby_gas_stations(self, location: Tuple[float, float], radius_meters: int, max_count: int = 20) -> List[Dict]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.businessStatus,routingSummaries"
        }

        payload = {
            "includedTypes": ["gas_station"],
            "maxResultCount": max_count,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": location[0], "longitude": location[1]},
                    "radius": float(radius_meters)
                }
            },
            "routingParameters": {
                "origin": {"latitude": location[0], "longitude": location[1]},
                "travelMode": "TWO_WHEELER"
            }
        }

        try:
            response = await self.client.post(self.places_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            logger.error(f"Erro ao buscar postos: {e}")
            return []

        places = data.get('places', [])
        routings = data.get('routingSummaries', [])

        results = []
        for i in range(len(places)):
            place = places[i]
            if i < len(routings) and routings[i].get('legs'):
                place_data = {
                    **place,
                    'distanceMeters': routings[i]['legs'][0].get('distanceMeters')
                }
                results.append(place_data)

        return results
