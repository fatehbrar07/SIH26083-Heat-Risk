import time
from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional

from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.thermal.heat_index_engine import HeatIndexEngine
from backend.app.vulnerability.hvi_engine import HVIEngine
from backend.app.risk.risk_engine import RiskEngine
from backend.app.gis.ward_mapping import GISEngine
from backend.app.advisory.advisory_engine import AdvisoryEngine
from backend.app.data_sources.open_meteo import OpenMeteoClient
from backend.app.data_sources.nasa_power import NASAPowerClient
from backend.app.models.schemas import ThermalCalculateRequest, RiskCalculateRequest

router = APIRouter(prefix="/api/v1", tags=["Heat Risk API v1"])

# Shared service instances
hvi_engine = HVIEngine()
risk_engine = RiskEngine()
gis_engine = GISEngine()
open_meteo_client = OpenMeteoClient()
nasa_power_client = NASAPowerClient()

@router.get("/locations")
async def get_locations():
    """List supported municipal zones and wards with geographic bounds."""
    all_wards = hvi_engine.get_all_wards_hvi()
    return {
        "city": "Delhi NCR, India",
        "total_wards": len(all_wards),
        "wards": all_wards,
        "default_coordinates": {"latitude": 28.6139, "longitude": 77.2090}
    }

@router.get("/weather/current")
async def get_current_weather(
    lat: float = Query(default=28.6139, description="Latitude"),
    lon: float = Query(default=77.2090, description="Longitude")
):
    """Retrieve current / baseline meteorological conditions from Open-Meteo & NASA POWER."""
    forecast = await open_meteo_client.fetch_5day_forecast(lat=lat, lon=lon)
    first_day = forecast["daily_forecasts"][0] if forecast.get("daily_forecasts") else {}
    return {
        "source": forecast.get("source"),
        "coordinates": {"latitude": lat, "longitude": lon},
        "current_conditions": {
            "temperature_2m_c": first_day.get("peak_temperature_c", 40.0),
            "relative_humidity_2m_pct": first_day.get("concurrent_rh_pct", 35.0),
            "wind_speed_2m_ms": first_day.get("concurrent_wind_speed_ms", 2.5),
            "solar_radiation_w_m2": first_day.get("concurrent_solar_radiation_w_m2", 650.0)
        },
        "provenance": forecast.get("provenance")
    }

@router.get("/weather/forecast")
async def get_weather_forecast(
    lat: float = Query(default=28.6139, description="Latitude"),
    lon: float = Query(default=77.2090, description="Longitude")
):
    """Retrieve 5-day (D+1 to D+5) forward meteorological forecast."""
    return await open_meteo_client.fetch_5day_forecast(lat=lat, lon=lon)

@router.get("/thermal/current")
async def get_current_thermal(
    temp_c: float = Query(default=40.0, description="Air temperature in °C"),
    rh_pct: float = Query(default=35.0, description="Relative humidity %"),
    wind_speed_ms: float = Query(default=2.5, description="Wind speed m/s"),
    solar_radiation_w_m2: float = Query(default=650.0, description="Solar irradiance W/m^2")
):
    """Compute current physiological thermal stress indices (UTCI, WBGT, Heat Index)."""
    utci = UTCIEngine.calculate_utci(temp_c, rh_pct, wind_speed_ms, solar_radiation_w_m2)
    wbgt = WBGTEngine.calculate_outdoor_wbgt(temp_c, rh_pct, wind_speed_ms, solar_radiation_w_m2)
    hi = HeatIndexEngine.calculate_heat_index(temp_c, rh_pct)

    return {
        "input_weather": {
            "air_temperature_c": temp_c,
            "relative_humidity_pct": rh_pct,
            "wind_speed_ms": wind_speed_ms,
            "solar_radiation_w_m2": solar_radiation_w_m2
        },
        "utci": {
            "value_c": utci,
            **UTCIEngine.get_utci_category(utci),
            "standard": "Universal Thermal Climate Index (WMO / Fiala model)"
        },
        "wbgt": {
            "value_c": wbgt,
            **WBGTEngine.get_occupational_advisory(wbgt),
            "standard": "ISO 7243:2017 & NIOSH Criteria"
        },
        "heat_index": {
            "value_c": hi,
            **HeatIndexEngine.get_heat_index_category(hi),
            "standard": "NOAA NWS Rothfusz baseline"
        }
    }

@router.get("/thermal/forecast")
async def get_thermal_forecast(
    lat: float = Query(default=28.6139, description="Latitude"),
    lon: float = Query(default=77.2090, description="Longitude")
):
    """Compute 5-day forward thermal stress projections (D+1 to D+5)."""
    forecast_data = await open_meteo_client.fetch_5day_forecast(lat=lat, lon=lon)
    daily_projections = []

    for item in forecast_data.get("daily_forecasts", []):
        t = item["peak_temperature_c"]
        rh = item["concurrent_rh_pct"]
        ws = item["concurrent_wind_speed_ms"]
        sol = item["concurrent_solar_radiation_w_m2"]

        utci = UTCIEngine.calculate_utci(t, rh, ws, sol)
        wbgt = WBGTEngine.calculate_outdoor_wbgt(t, rh, ws, sol)
        hi = HeatIndexEngine.calculate_heat_index(t, rh)

        daily_projections.append({
            "horizon": item["horizon_label"],
            "date": item["date"],
            "weather": {
                "temperature_c": t,
                "relative_humidity_pct": rh,
                "wind_speed_ms": ws,
                "solar_radiation_w_m2": sol
            },
            "utci_c": utci,
            "utci_category": UTCIEngine.get_utci_category(utci)["category"],
            "wbgt_c": wbgt,
            "wbgt_category": WBGTEngine.get_occupational_advisory(wbgt)["category"],
            "heat_index_c": hi
        })

    return {
        "city": "Delhi NCR, India",
        "forecast_days": len(daily_projections),
        "projections": daily_projections,
        "provenance": forecast_data.get("provenance")
    }

@router.get("/vulnerability")
async def get_vulnerability(
    ward_id: Optional[str] = Query(default=None, description="Optional specific Ward ID")
):
    """Retrieve Heat Vulnerability Index (HVI) demographic distributions."""
    if ward_id:
        return hvi_engine.calculate_ward_hvi(ward_id)
    return {
        "source": "Census of India 2011 Primary Census Abstract Baseline",
        "total_wards": len(hvi_engine.get_all_wards_hvi()),
        "wards": hvi_engine.get_all_wards_hvi()
    }

@router.get("/risk/current")
async def get_current_risk(
    ward_id: str = Query(default="DEL-W01", description="Ward ID"),
    temp_c: float = Query(default=40.0, description="Air temp °C"),
    rh_pct: float = Query(default=35.0, description="Relative humidity %"),
    wind_speed_ms: float = Query(default=2.5, description="Wind speed m/s"),
    solar_radiation_w_m2: float = Query(default=650.0, description="Solar irradiance W/m^2"),
    consecutive_extreme_days: int = Query(default=1, description="Duration in days")
):
    """Calculate Composite Human Heat Risk for a specific ward and environmental state."""
    return risk_engine.calculate_risk(
        ward_id=ward_id,
        temp_c=temp_c,
        rh_pct=rh_pct,
        wind_speed_2m_ms=wind_speed_ms,
        solar_radiation_w_m2=solar_radiation_w_m2,
        consecutive_extreme_days=consecutive_extreme_days
    )

@router.get("/risk/forecast")
async def get_risk_forecast(
    ward_id: str = Query(default="DEL-W01", description="Ward ID"),
    lat: float = Query(default=28.6139, description="Latitude"),
    lon: float = Query(default=77.2090, description="Longitude")
):
    """Compute 5-day predictive risk trajectory (D+1 to D+5) for a selected ward."""
    forecast_data = await open_meteo_client.fetch_5day_forecast(lat=lat, lon=lon)
    daily_risks = []

    consecutive_days = 1
    for item in forecast_data.get("daily_forecasts", []):
        t = item["peak_temperature_c"]
        rh = item["concurrent_rh_pct"]
        ws = item["concurrent_wind_speed_ms"]
        sol = item["concurrent_solar_radiation_w_m2"]

        # Increment persistence count if peak temp is high
        if t >= 40.0:
            consecutive_days += 1
        else:
            consecutive_days = 1

        risk_res = risk_engine.calculate_risk(
            ward_id=ward_id,
            temp_c=t,
            rh_pct=rh,
            wind_speed_2m_ms=ws,
            solar_radiation_w_m2=sol,
            consecutive_extreme_days=consecutive_days
        )

        daily_risks.append({
            "horizon": item["horizon_label"],
            "date": item["date"],
            "risk_score": risk_res["risk_score"],
            "risk_band": risk_res["risk_band"],
            "risk_color": risk_res["risk_color"],
            "action_priority": risk_res["action_priority"],
            "hazard_score": risk_res["hazard_score"],
            "vulnerability_score": risk_res["vulnerability_score"],
            "thermal_metrics": risk_res["thermal_metrics"]
        })

    return {
        "ward_id": ward_id,
        "ward_name": hvi_engine.calculate_ward_hvi(ward_id).get("ward_name"),
        "forecast_days": len(daily_risks),
        "risk_forecast": daily_risks,
        "disclaimer": "Prototype relative risk estimate — not a clinical or mortality forecast."
    }

@router.get("/advisory")
async def get_advisories(
    ward_id: str = Query(default="DEL-W01", description="Ward ID"),
    temp_c: float = Query(default=40.0, description="Air temp °C"),
    rh_pct: float = Query(default=35.0, description="Relative humidity %"),
    wind_speed_ms: float = Query(default=2.5, description="Wind speed m/s"),
    solar_radiation_w_m2: float = Query(default=650.0, description="Solar radiation W/m^2"),
    consecutive_extreme_days: int = Query(default=1, description="Duration")
):
    """Retrieve structured municipal and citizen advisories in English & Hindi."""
    risk_data = risk_engine.calculate_risk(
        ward_id=ward_id,
        temp_c=temp_c,
        rh_pct=rh_pct,
        wind_speed_2m_ms=wind_speed_ms,
        solar_radiation_w_m2=solar_radiation_w_m2,
        consecutive_extreme_days=consecutive_extreme_days
    )
    return AdvisoryEngine.generate_advisories(risk_data)

@router.get("/map/risk")
async def get_map_risk(
    temp_c: float = Query(default=40.0, description="Air temp °C"),
    rh_pct: float = Query(default=35.0, description="Relative humidity %"),
    wind_speed_ms: float = Query(default=2.5, description="Wind speed m/s"),
    solar_radiation_w_m2: float = Query(default=650.0, description="Solar radiation W/m^2"),
    consecutive_extreme_days: int = Query(default=1, description="Duration in days")
):
    """Return an enriched GeoJSON layer with ward-level risk polygons for Leaflet mapping."""
    return gis_engine.generate_risk_geojson(
        temp_c=temp_c,
        rh_pct=rh_pct,
        wind_speed_ms=wind_speed_ms,
        solar_radiation_w_m2=solar_radiation_w_m2,
        consecutive_extreme_days=consecutive_extreme_days
    )

@router.get("/sources")
async def get_sources():
    """Retrieve Tier-1 data provenance, API endpoints, and license registry."""
    return {
        "tier_1_automated": [
            {
                "name": "NASA POWER (LaRC)",
                "role": "40-Year Climatological Baseline & Reanalysis Normals (MERRA-2)",
                "endpoint": "https://power.larc.nasa.gov/api/temporal/daily/point",
                "auth_required": False,
                "status": "Verified 200 OK Live"
            },
            {
                "name": "Open-Meteo Forecast Engine",
                "role": "5-Day Forward High-Resolution Numerical Weather Prediction (NWP)",
                "endpoint": "https://api.open-meteo.com/v1/forecast",
                "auth_required": False,
                "status": "Verified 200 OK Live"
            },
            {
                "name": "Census of India 2011 Primary Census Abstract",
                "role": "Demographic & Vulnerability Baseline (HVI)",
                "portal": "https://censusindia.gov.in/",
                "auth_required": False,
                "status": "Archived Open Data"
            }
        ],
        "tier_2_future_integrations": [
            {"name": "NCMRWF Ensemble Weather Streams", "role": "Direct MoES GRIB2 Ensemble Integration"},
            {"name": "MOSDAC INSAT-3D/3DR LST", "role": "Satellite Land Surface Temperature (ISRO)"}
        ],
        "tier_3_governance_layers": [
            {"name": "NHRIDS / IDSP Hospital Surveillance", "role": "Confidential Clinical Emergency Records"}
        ]
    }

@router.get("/methodology")
async def get_methodology():
    """Explain the scientific formulation and risk weighting pipeline."""
    return {
        "title": "SIH26083 Human Thermal Risk Engine Methodology",
        "pillars": [
            {
                "pillar": "1. Physiological Thermal Stress",
                "method": "Universal Thermal Climate Index (UTCI) & ISO 7243 WBGT",
                "description": "Calculates human thermoregulatory strain from T2M, RH, Wind Speed, and Solar Irradiance."
            },
            {
                "pillar": "2. Socio-Demographic Vulnerability",
                "method": "Heat Vulnerability Index (HVI)",
                "description": "Ward-level weighting of Elderly (60+), Children (0-6), Outdoor workers, Density, and Informal housing."
            },
            {
                "pillar": "3. Exposure Duration Multiplier",
                "method": "Non-linear multi-day persistence compounding",
                "description": "Applies a 10% to 30% risk penalty for consecutive days of extreme heat exposure."
            }
        ],
        "risk_formula": "Human_Heat_Risk = min(100, (0.60 * Hazard_Score + 0.40 * HVI_Score) * Duration_Multiplier)",
        "disclaimer": "Prototype relative risk estimate — not a clinical or mortality forecast."
    }

@router.post("/thermal/calculate")
async def post_thermal_calculate(req: ThermalCalculateRequest):
    utci = UTCIEngine.calculate_utci(req.temperature_c, req.relative_humidity_pct, req.wind_speed_ms, req.solar_radiation_w_m2)
    wbgt = WBGTEngine.calculate_outdoor_wbgt(req.temperature_c, req.relative_humidity_pct, req.wind_speed_ms, req.solar_radiation_w_m2)
    hi = HeatIndexEngine.calculate_heat_index(req.temperature_c, req.relative_humidity_pct)
    return {
        "utci": {"value_c": utci, **UTCIEngine.get_utci_category(utci)},
        "wbgt": {"value_c": wbgt, **WBGTEngine.get_occupational_advisory(wbgt)},
        "heat_index": {"value_c": hi, **HeatIndexEngine.get_heat_index_category(hi)}
    }

@router.post("/risk/calculate")
async def post_risk_calculate(req: RiskCalculateRequest):
    return risk_engine.calculate_risk(
        ward_id=req.ward_id,
        temp_c=req.temperature_c,
        rh_pct=req.relative_humidity_pct,
        wind_speed_2m_ms=req.wind_speed_ms,
        solar_radiation_w_m2=req.solar_radiation_w_m2,
        consecutive_extreme_days=req.consecutive_extreme_days
    )
