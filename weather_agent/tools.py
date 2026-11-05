import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: "sereno", 1: "prevalentemente sereno", 2: "parzialmente nuvoloso",
    3: "coperto", 45: "nebbia", 48: "nebbia con brina",
    51: "pioviggine leggera", 53: "pioviggine moderata", 55: "pioviggine intensa",
    61: "pioggia leggera", 63: "pioggia moderata", 65: "pioggia intensa",
    71: "neve leggera", 73: "neve moderata", 75: "neve intensa",
    80: "rovesci leggeri", 81: "rovesci moderati", 82: "rovesci violenti",
    95: "temporale", 96: "temporale con grandine", 99: "temporale con grandine intensa",
}


def get_weather(city: str) -> dict:
    """Restituisce meteo attuale e previsioni per le prossime 12 ore.

    Args:
        city: Nome della città, per esempio Roma o Milano.
    """
    city = city.strip() if isinstance(city, str) else ""
    if not city:
        return {"ok": False, "error": "nome della città non valido"}

    try:
        geo_resp = httpx.get(GEOCODING_URL, params={
            "name": city, "count": 1, "language": "it", "format": "json"
        }, timeout=8.0)
        geo_resp.raise_for_status()
        locations = geo_resp.json().get("results", [])
        if not locations:
            return {"ok": False, "error": "città non trovata"}

        place = locations[0]
        latitude, longitude = float(place["latitude"]), float(place["longitude"])
        is_italy = place.get("country_code") == "IT"
        model_name = "italia_meteo_arpae_icon_2i" if is_italy else "best_match"

        forecast_resp = httpx.get(FORECAST_URL, params={
            "latitude": latitude,
            "longitude": longitude,
            "models": model_name,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "precipitation,rain,weather_code"
            ),
            "hourly": (
                "temperature_2m,precipitation_probability,apparent_temperature,"
                "rain,relative_humidity_2m,weather_code"
            ),
            "timezone": "auto",
            "forecast_hours": 12,
        }, timeout=8.0)
        forecast_resp.raise_for_status()
        data = forecast_resp.json()

        current = data["current"]
        hourly = data["hourly"]

        # costruisco la previsione a 12 ore
        hourly_forecast = [
            {
                "time": time,
                "temperature_c": temp,
                "apparent_temperature_c": app_temp,
                "humidity_percent": humidity,
                "rain_mm": rain,
                "precipitation_probability_percent": prob,
                "condition": WEATHER_CODES.get(int(code), f"codice WMO {code}"),
            }
            for time, temp, app_temp, humidity, rain, prob, code in zip(
                hourly["time"],
                hourly["temperature_2m"],
                hourly["apparent_temperature"],
                hourly["relative_humidity_2m"],
                hourly["rain"],
                hourly["precipitation_probability"],
                hourly["weather_code"],
            )
        ][:12]

        code = int(current["weather_code"])
        # ritorna JSON con i dati strutturati per l'LLM
        return {
            "ok": True,
            "city": place.get("name", city),
            "country": place.get("country"),
            "timezone": data.get("timezone"),
            "current": {
                "observed_at": current["time"],
                "temperature_c": current["temperature_2m"],
                "apparent_temperature_c": current["apparent_temperature"],
                "humidity_percent": current["relative_humidity_2m"],
                "precipitation_mm": current["precipitation"],
                "rain_mm": current["rain"],
                "condition": WEATHER_CODES.get(code, f"codice WMO {code}"),
            },
            "next_12_hours": hourly_forecast,
            "source": f"Open-Meteo ({model_name})" if model_name != "best_match" else "Open-Meteo",
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return {"ok": False, "error": "servizio meteo temporaneamente non disponibile"}

