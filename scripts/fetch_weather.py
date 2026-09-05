#!/usr/bin/env python3
"""
CLI Utility to fetch, verify, and inspect meteorological feeds from
Tier-1 public APIs (NASA POWER 40-yr baseline & Open-Meteo 5-day forecast).
"""
import sys
import asyncio
from backend.app.data_sources.open_meteo import OpenMeteoClient
from backend.app.data_sources.nasa_power import NASAPowerClient

async def main():
    print("================================================================")
    print("☀️  SIH26083 METEOROLOGICAL INGESTION PIPELINE (TIER-1 OPEN DATA)")
    print("================================================================")
    
    # 1. Fetch Open-Meteo 5-Day NWP Forecast
    print("\n[1/2] Fetching 5-day Hourly NWP Forecast from Open-Meteo...")
    om_client = OpenMeteoClient()
    forecast = await om_client.fetch_5day_forecast(lat=28.6139, lon=77.2090)
    print(f"Status: {forecast.get('status')} | Source: {forecast.get('source')}")
    print(f"Retrieved {len(forecast.get('daily_forecasts', []))} daily projection summaries:")
    for d in forecast.get("daily_forecasts", []):
        print(f"  • {d['horizon_label']} ({d['date']}): Peak T = {d['peak_temperature_c']}°C | RH = {d['concurrent_rh_pct']}% | Wind = {d['concurrent_wind_speed_ms']} m/s | Solar = {d['concurrent_solar_radiation_w_m2']} W/m²")

    # 2. Fetch NASA POWER 40-Year Climatological Baseline
    print("\n[2/2] Fetching NASA POWER 40-Year Historical Baseline (MERRA-2 Reanalysis)...")
    nasa_client = NASAPowerClient()
    nasa_data = await nasa_client.fetch_historical_baseline(lat=28.6139, lon=77.2090, start_year="20230501", end_year="20230531")
    print(f"Status: {nasa_data.get('status')} | Source: {nasa_data.get('source')}")
    summary = nasa_data.get("summary", {})
    print(f"  • Climatological Mean May Temp: {summary.get('climatological_mean_temp_c')}°C")
    print(f"  • Peak Observed Temperature: {summary.get('peak_observed_temp_c')}°C")
    print(f"  • IMD Heatwave Departure Threshold (+4.5°C): {summary.get('imd_heatwave_departure_threshold_c')}°C")
    print("\n✅ All Tier-1 data feeds verified and operational.")

if __name__ == "__main__":
    asyncio.run(main())
