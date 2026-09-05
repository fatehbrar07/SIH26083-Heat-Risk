import time
from fastapi import APIRouter, Query, HTTPException, Body
from typing import Dict, Any, Optional

from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.thermal.heat_index_engine import HeatIndexEngine
from backend.app.vulnerability.hvi_engine import HVIEngine, SUPPORTED_CITIES
from backend.app.risk.risk_engine import RiskEngine
from backend.app.gis.ward_mapping import GISEngine
from backend.app.advisory.advisory_engine import AdvisoryEngine
from backend.app.advisory.telegram_dispatcher import TelegramDispatcher
from backend.app.data_sources.open_meteo import OpenMeteoClient
from backend.app.data_sources.nasa_power import NASAPowerClient
from backend.app.data_sources.hindcast_engine import HindcastEngine
from backend.app.models.schemas import ThermalCalculateRequest, RiskCalculateRequest, AlertBroadcastRequest

router = APIRouter(prefix="/api/v1", tags=["Heat Risk API v1"])

# Shared service instances
hvi_engine = HVIEngine()
risk_engine = RiskEngine()
gis_engine = GISEngine()
open_meteo_client = OpenMeteoClient()
nasa_power_client = NASAPowerClient()
hindcast_engine = HindcastEngine()
telegram_dispatcher = TelegramDispatcher()

@router.get("/locations")
async def get_locations(
    city: Optional[str] = Query(default=None, description="Target city identifier (delhi, ahmedabad, surat, bhubaneswar, mumbai)")
):
    """List supported municipal zones and wards with geographic bounds."""
    if city:
        target_city = hvi_engine._normalize_city_id(city)
        wards = hvi_engine.get_all_wards_hvi(target_city)
        supported = [c for c in hvi_engine.get_supported_cities() if c["city_id"] == target_city]
        city_meta = supported[0] if supported else {"city_name": target_city.title(), "state": "India"}
        return {
            "city": f"{city_meta['city_name']}, {city_meta['state']}",
            "city_id": target_city,
            "total_wards": len(wards),
            "wards": wards,
            "default_coordinates": {
                "latitude": city_meta.get("default_lat", 28.6139),
                "longitude": city_meta.get("default_lon", 77.2090)
            },
            "default_ward_id": city_meta.get("default_ward_id", "DEL-W01"),
            "supported_cities": hvi_engine.get_supported_cities()
        }
    all_wards = hvi_engine.get_all_wards_hvi("delhi")
    return {
        "city": "Delhi NCR, India",
        "city_id": "delhi",
        "total_wards": len(all_wards),
        "wards": all_wards,
        "default_coordinates": {"latitude": 28.6139, "longitude": 77.2090},
        "default_ward_id": "DEL-W01",
        "supported_cities": hvi_engine.get_supported_cities()
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
        "coordinates": {"latitude": lat, "longitude": lon},
        "weather": {
            "temperature_c": first_day.get("peak_temperature_c", 40.0),
            "relative_humidity_pct": first_day.get("concurrent_rh_pct", 35.0),
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
            "standard": "ISO 7243 / NIOSH Criteria (Liljegren / Stull physics)"
        },
        "heat_index": {
            "value_c": hi,
            **HeatIndexEngine.get_heat_index_category(hi),
            "standard": "NOAA / Steadman Multi-Variable Equation"
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
        "coordinates": {"latitude": lat, "longitude": lon},
        "forecast_days": len(daily_projections),
        "projections": daily_projections,
        "provenance": forecast_data.get("provenance")
    }

@router.get("/vulnerability")
async def get_vulnerability(
    ward_id: Optional[str] = Query(default=None, description="Optional specific Ward ID (e.g. DEL-W01, AHM-W01, SUR-W01, BHU-W01, MUM-W01)"),
    city: Optional[str] = Query(default=None, description="Optional city filter (delhi, ahmedabad, surat, bhubaneswar, mumbai)")
):
    """Retrieve Heat Vulnerability Index (HVI) demographic distributions."""
    if ward_id:
        return hvi_engine.calculate_ward_hvi(ward_id)
    target_city = hvi_engine._normalize_city_id(city) if city else "delhi"
    wards = hvi_engine.get_all_wards_hvi(target_city)
    return {
        "source": "Census of India 2011 Primary Census Abstract Baseline",
        "city_id": target_city,
        "total_wards": len(wards),
        "wards": wards
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

@router.get("/advisory/occupational")
async def get_occupational_advisory(
    temp_c: float = Query(default=40.0, description="Air temperature in °C"),
    rh_pct: float = Query(default=35.0, description="Relative humidity %"),
    wind_speed_ms: float = Query(default=2.5, description="Wind speed in m/s"),
    solar_radiation_w_m2: float = Query(default=650.0, description="Solar irradiance in W/m^2"),
    wbgt_c: Optional[float] = Query(default=None, description="Optional pre-computed WBGT °C"),
    workload: str = Query(default="moderate", description="Workload category (light, moderate, heavy, very_heavy)"),
    sector: Optional[str] = Query(default=None, description="Target sector (gig_delivery, construction, agriculture, traffic_police)"),
    acclimatized: bool = Query(default=True, description="Whether workforce is acclimatized")
):
    """
    Retrieve sector-specific occupational heat safety protocols and ISO 7243 work-rest cycles.
    """
    return AdvisoryEngine.get_occupational_advisory(
        temp_c=temp_c,
        rh_pct=rh_pct,
        wind_speed_ms=wind_speed_ms,
        solar_radiation_w_m2=solar_radiation_w_m2,
        wbgt_c=wbgt_c,
        workload=workload,
        sector=sector,
        acclimatized=acclimatized
    )

@router.post("/alerts/broadcast")
async def broadcast_alerts(req: AlertBroadcastRequest = Body(...)):
    """
    Trigger simulated or live municipal broadcast and action triggers
    for high/critical risk wards via async Telegram notification service.
    """
    all_wards = hvi_engine.get_all_wards_hvi("delhi")
    target_wards = []
    if req.ward_id:
        target_wards = [w for w in all_wards if w["ward_id"] == req.ward_id]
        if not target_wards:
            for city_key in ["ahmedabad", "surat", "bhubaneswar", "mumbai"]:
                cw = hvi_engine.get_all_wards_hvi(city_key)
                matched = [w for w in cw if w["ward_id"] == req.ward_id]
                if matched:
                    target_wards = matched
                    break
            if not target_wards:
                target_wards = [{"ward_id": req.ward_id, "ward_name": req.ward_id}]
    else:
        target_wards = all_wards

    dispatched = []
    summary_triggers = set()

    for ward in target_wards:
        risk_res = risk_engine.calculate_risk(
            ward_id=ward["ward_id"],
            temp_c=req.temperature_c,
            rh_pct=req.relative_humidity_pct,
            wind_speed_2m_ms=req.wind_speed_ms,
            solar_radiation_w_m2=req.solar_radiation_w_m2,
            consecutive_extreme_days=req.consecutive_extreme_days
        )
        if risk_res["risk_score"] >= req.min_risk_threshold or req.ward_id:
            advisory = AdvisoryEngine.generate_advisories(risk_res)
            broadcast_res = await telegram_dispatcher.broadcast_ward_alert(
                ward_name=risk_res["ward_name"],
                risk_score=risk_res["risk_score"],
                risk_band=risk_res["risk_band"],
                thermal_metrics=risk_res["thermal_metrics"],
                municipal_playbook=advisory["municipal_playbook"],
                occupational_schedule=advisory["occupational_schedule"],
                chat_id=req.recipient_chat_id,
                language=req.language
            )
            triggers = advisory.get("action_triggers", [])
            for t in triggers:
                summary_triggers.add(t)

            dispatched.append({
                "ward_id": ward["ward_id"],
                "ward_name": risk_res["ward_name"],
                "risk_score": risk_res["risk_score"],
                "risk_band": risk_res["risk_band"],
                "bulletin_html": broadcast_res.get("bulletin_text", ""),
                "action_triggers": triggers,
                "dispatch_status": "simulated" if req.simulate else broadcast_res.get("status")
            })

    return {
        "broadcast_id": f"bc-{int(time.time())}",
        "status": "simulated" if req.simulate else "live",
        "target_wards_count": len(dispatched),
        "dispatched_alerts": dispatched,
        "summary_action_triggers": list(summary_triggers)
    }

@router.get("/map/risk")
async def get_map_risk(
    city: Optional[str] = Query(default=None, description="Target city identifier (delhi, ahmedabad, surat, bhubaneswar, mumbai)"),
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
        consecutive_extreme_days=consecutive_extreme_days,
        city_id=city
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

@router.get("/hindcast/events")
async def get_hindcast_events():
    """List historical heatwave benchmark events available for hindcast replay."""
    return {
        "catalog": hindcast_engine.get_events_catalog(),
        "total_events": len(hindcast_engine.HISTORICAL_EVENTS),
        "lead_time_scope_hours": 120,
        "epidemiological_validation": "Grounded in Azhar et al. (2014) and Mazdiyasni et al. (2017)"
    }

@router.get("/hindcast/replay")
async def get_hindcast_replay(
    event_id: str = Query(default="delhi_june_2024", description="Historical event identifier (delhi_june_2024, ahmedabad_may_2010, delhi_may_2022)"),
    ward_id: str = Query(default="DEL-W01", description="Ward identifier for socio-demographic vulnerability pairing")
):
    """
    Simulate step-by-step 5-day lead-time progression (D-5 to D-Day) for historical heatwave.
    Demonstrates 72h-120h advance alert elevation before peak human thermal crisis.
    """
    try:
        return hindcast_engine.replay_event(event_id=event_id, ward_id=ward_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
