import time
import asyncio
import httpx
from typing import Optional, Dict, Any

# --- Simple in-memory TTL cache (biar hemat call API gratisan)
_CACHE: Dict[str, Dict[str, Any]] = {}
_TTL_SECONDS = 5 * 60  # 5 menit

async def _fetch_json(client: httpx.AsyncClient, url: str, params: dict) -> dict:
    r = await client.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

async def get_weather_by_city(city: str, lang: str = "en") -> Optional[dict]:
    cache_key = f"{city.lower()}|{lang}"
    now = time.time()

    # serve from cache kalau masih fresh
    if cache_key in _CACHE and now - _CACHE[cache_key]["ts"] < _TTL_SECONDS:
        return _CACHE[cache_key]["data"]

    async with httpx.AsyncClient() as client:
        # 1) Geocoding: cari lat/lon dari nama kota
        geocode = await _fetch_json(
            client,
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": city, "count": 1, "language": lang, "format": "json"},
        )

        results = geocode.get("results") or []
        if not results:
            return None
        loc = results[0]
        lat, lon, city_name, country = loc["latitude"], loc["longitude"], loc["name"], loc.get("country")

        # 2) Weather: ambil cuaca current + hourly ringkas
        weather = await _fetch_json(
            client,
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
                "timezone": "auto",
            },
        )

        current = weather.get("current_weather", {})
        hourly = weather.get("hourly", {})

        # 3) Bentuk payload sederhana & enak dikonsumsi front-end
        payload = {
            "location": {
                "city": city_name,
                "country": country,
                "latitude": lat,
                "longitude": lon,
            },
            "current": {
                "time": current.get("time"),
                "temperature_c": current.get("temperature"),
                "windspeed_kmh": current.get("windspeed"),
                "winddirection_deg": current.get("winddirection"),
                "weathercode": current.get("weathercode"),
            },
            "hourly": {
                "time": hourly.get("time", [])[:24],
                "temperature_c": (hourly.get("temperature_2m", [])[:24]),
                "precipitation_mm": (hourly.get("precipitation", [])[:24]),
                "humidity_pct": (hourly.get("relative_humidity_2m", [])[:24]),
                "wind_speed_kmh": (hourly.get("wind_speed_10m", [])[:24]),
            },
            "source": "open-meteo.com",
            "cached": False,
        }

        _CACHE[cache_key] = {"ts": now, "data": payload}
        return payload