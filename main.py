import os

from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from gateway import GoogleMapsGateway
from schemas import RouteResponse, RouteRequest, RouteStops, RouteWarning, TimelineEvent
from utils import decode_route_points, calculate_distance, generate_google_maps_url

MAX_RADIUS = 50000


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await gmaps_gateway.close()

app = FastAPI(lifespan=lifespan)
gmaps_gateway = GoogleMapsGateway(api_key=os.getenv('GOOGLE_API_KEY'))


@app.post("/route-plan", response_model=RouteResponse)
async def route_plan(request: RouteRequest):
    # 1. Obter a rota de motocicleta
    route_data = await gmaps_gateway.get_motorcycle_route(request.origin, request.destination)
    if not route_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Rota não encontrada")

    encoded_polyline = route_data['polyline']['encodedPolyline']
    route_points = decode_route_points(encoded_polyline)
    total_distance_km = round(route_data['distanceMeters'] / 1000, 2)

    fuel_required_coords = []
    acc_distance = 0.0
    fuel_limit = request.motorcycle.fuel_autonomy - request.motorcycle.fuel_safety_margin

    # 2. Identificar os "pontos de parada" (triggers) em memória
    for i in range(len(route_points) - 1):
        segment_dist = calculate_distance(route_points[i], route_points[i + 1])
        acc_distance += segment_dist

        if acc_distance >= fuel_limit:
            fuel_required_coords.append(route_points[i + 1])
            acc_distance = 0.0

    radius_meters = min(MAX_RADIUS, int(request.motorcycle.fuel_safety_margin * 1000))
    current_segment_start = 0.0
    timeline = []

    # 3. Itera sobre as coordenadas de parada requeridas
    for idx, coord in enumerate(fuel_required_coords):
        gas_stations = await gmaps_gateway.find_nearby_gas_stations(coord, radius_meters)
        current_segment_end = current_segment_start + fuel_limit

        found_stop = False
        if gas_stations:
            # 4. Ordena postos por proximidade
            gas_stations.sort(key=lambda x: x.get('distanceMeters', float('inf')))

            # 5. Itera sobre cada um dos postos encontrados
            for station in gas_stations:
                if station.get('businessStatus') != 'OPERATIONAL':
                    continue

                dist_km = station.get('distanceMeters') / 1000
                if dist_km <= request.motorcycle.fuel_safety_margin:
                    timeline.append(TimelineEvent(type="STOP", start_km=round(current_segment_start, 2), end_km=round(current_segment_end, 2), data=RouteStops(
                        name=station['displayName']['text'],
                        address=station.get('formattedAddress', ''),
                        coordinates={
                            "lat": station['location']['latitude'],
                            "lng": station['location']['longitude']
                        }
                    )))
                    found_stop = True
                    break

        # 6. Se não encontrar, emite um alerta
        if not found_stop:
            start_problem = (idx + 1) * fuel_limit
            end_problem = start_problem + request.motorcycle.fuel_safety_margin

            timeline.append(TimelineEvent(type="WARNING", start_km=start_problem, end_km=end_problem, data=RouteWarning(
                message=f"Atenção: Nenhum posto operacional encontrado próximo ao KM {start_problem:.2f}.",
                coordinates={"lat": coord[0], "lng": coord[1]}
            )))

        # 7. Reseta o segmento de controle
        current_segment_start = current_segment_end

    timeline.sort(key=lambda x: x.end_km)

    # 8. URL de Navegação
    nav_url = generate_google_maps_url(
        origin=request.origin,
        destination=request.destination,
        timeline=timeline
    )

    return RouteResponse(
        total_distance_km=total_distance_km,
        google_maps_url=nav_url,
        timeline=timeline
    )
