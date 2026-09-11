import httpx
import time
from typing import Dict, Any, Optional

WMO_WEATHER_CODES = {
    0: ("Clear sky", "साफ आसमान"),
    1: ("Mainly clear", "मुख्यतः साफ"),
    2: ("Partly cloudy", "आंशिक रूप से बादल"),
    3: ("Overcast", "घने बादल"),
    45: ("Fog", "कोहरा"),
    48: ("Depositing rime fog", "घना कोहरा"),
    51: ("Light drizzle", "हल्की बूंदाबांदी"),
    53: ("Moderate drizzle", "मध्यम बूंदाबांदी"),
    55: ("Dense drizzle", "घनी बूंदाबांदी"),
    61: ("Slight rain", "हल्की बारिश"),
    63: ("Moderate rain", "मध्यम बारिश"),
    65: ("Heavy rain", "भारी बारिश"),
    71: ("Slight snow", "हल्की बर्फबारी"),
    73: ("Moderate snow", "मध्यम बर्फबारी"),
    75: ("Heavy snow", "भारी बर्फबारी"),
    80: ("Slight rain showers", "हल्की बौछारें"),
    81: ("Moderate rain showers", "मध्यम बौछारें"),
    82: ("Violent rain showers", "तीव्र बौछारें"),
    95: ("Thunderstorm", "गरज के साथ तूफान"),
    96: ("Thunderstorm with slight hail", "आंधी-तूफान व ओलावृष्टि"),
    99: ("Thunderstorm with heavy hail", "भारी ओलावृष्टि व तूफान")
}

class OpenMeteoClient:
    """
    Tier-1 Real-World Live Weather Forecast Ingestion Client for Open-Meteo.
    Provides real-time live weather conditions and 7-day hourly high-resolution Numerical Weather Prediction data.
    Keyless, open government-standard WMO REST API.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: float = 0.0

    async def fetch_live_weather(
        self,
        lat: float = 28.6139,
        lon: float = 77.2090
    ) -> Dict[str, Any]:
        """
        Fetch real-time live atmospheric observation and 5-day hourly forecast directly from Open-Meteo.
        """
        now = time.time()
        cache_key = f"{round(lat, 4)}_{round(lon, 4)}"

        if cache_key in self._cache and (now - self._cache_timestamp) < self.cache_ttl:
            cached_res = self._cache[cache_key]
            cached_res["provenance"]["cache_hit"] = True
            return cached_res

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "surface_pressure",
                "direct_radiation",
                "diffuse_radiation",
                "shortwave_radiation",
                "uv_index"
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "wind_speed_10m",
                "direct_radiation",
                "uv_index"
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "uv_index_max",
                "precipitation_sum"
            ],
            "wind_speed_unit": "ms",
            "forecast_days": 5,
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        curr = data.get("current", {})
        w_code = curr.get("weather_code", 0)
        cond_en, cond_hi = WMO_WEATHER_CODES.get(w_code, ("Clear", "साफ"))

        result = {
            "status": "live",
            "coordinates": {"latitude": lat, "longitude": lon},
            "current": {
                "time": curr.get("time"),
                "temperature_c": float(curr.get("temperature_2m", 30.0)),
                "apparent_temperature_c": float(curr.get("apparent_temperature", 30.0)),
                "relative_humidity_pct": float(curr.get("relative_humidity_2m", 50.0)),
                "wind_speed_10m_ms": float(curr.get("wind_speed_10m", 2.0)),
                "wind_direction_deg": int(curr.get("wind_direction_10m", 0)),
                "solar_radiation_w_m2": float(curr.get("direct_radiation", 400.0)),
                "uv_index": float(curr.get("uv_index", 5.0)),
                "surface_pressure_hpa": float(curr.get("surface_pressure", 1013.0)),
                "weather_code": w_code,
                "condition": cond_en,
                "condition_hi": cond_hi
            },
            "daily_forecasts": self._format_daily_forecasts(data),
            "hourly_raw": data.get("hourly", {}),
            "provenance": {
                "source": "Open-Meteo High-Resolution Numerical Weather Prediction",
                "source_url": "https://open-meteo.com",
                "model_resolution": "0.1° (~11 km grid)",
                "data_tier": "Tier-1 Open Global API",
                "cache_hit": False,
                "timestamp": now
            }
        }

        self._cache[cache_key] = result
        self._cache_timestamp = now
        return result

    def _format_daily_forecasts(self, raw_data: Dict[str, Any]) -> list:
        daily = raw_data.get("daily", {})
        times = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        w_codes = daily.get("weather_code", [])
        uv_max = daily.get("uv_index_max", [])
        
        hourly = raw_data.get("hourly", {})
        h_t = hourly.get("temperature_2m", [])
        h_rh = hourly.get("relative_humidity_2m", [])
        h_ws = hourly.get("wind_speed_10m", [])
        h_rad = hourly.get("direct_radiation", [])

        forecasts = []
        for i, date_str in enumerate(times[:5]):
            peak_idx = min((i * 24) + 14, len(h_t) - 1) if h_t else 0
            code = w_codes[i] if i < len(w_codes) else 0
            cond_en, cond_hi = WMO_WEATHER_CODES.get(code, ("Clear", "साफ"))

            forecasts.append({
                "day_index": i + 1,
                "horizon": f"D+{i+1}",
                "date": date_str,
                "peak_temperature_c": float(t_max[i]) if i < len(t_max) else 35.0,
                "min_temperature_c": float(t_min[i]) if i < len(t_min) else 25.0,
                "concurrent_rh_pct": float(h_rh[peak_idx]) if h_rh and peak_idx < len(h_rh) else 50.0,
                "concurrent_wind_speed_ms": float(h_ws[peak_idx]) if h_ws and peak_idx < len(h_ws) else 2.5,
                "concurrent_solar_radiation_w_m2": float(h_rad[peak_idx]) if h_rad and peak_idx < len(h_rad) else 500.0,
                "uv_index_max": float(uv_max[i]) if i < len(uv_max) else 5.0,
                "weather_code": code,
                "condition": cond_en,
                "condition_hi": cond_hi
            })
        return forecasts

    async def fetch_5day_forecast(self, lat: float = 28.6139, lon: float = 77.2090) -> Dict[str, Any]:
        return await self.fetch_live_weather(lat=lat, lon=lon)
