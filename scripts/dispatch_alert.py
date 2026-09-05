#!/usr/bin/env python3
"""
Standalone Alert Dispatch Verification CLI.
Demonstrates simulated municipal broadcast and action trigger generation
for critical heatwave events (e.g., Delhi June 2024 heatwave surge).
"""
import asyncio
import json
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.advisory.telegram_dispatcher import TelegramDispatcher
from backend.app.advisory.advisory_engine import AdvisoryEngine
from backend.app.risk.risk_engine import RiskEngine
from backend.app.vulnerability.hvi_engine import HVIEngine

async def run_dispatch_simulation():
    print("=" * 70)
    print("🚨 SIH26083 MUNICIPAL HEATWAVE ALERT DISPATCH ENGINE")
    print("   Aligned with NDMA / NCDC / NIOSH Public Health Protocols")
    print("=" * 70)

    # 1. Initialize Engines
    hvi_engine = HVIEngine()
    risk_engine = RiskEngine()
    dispatcher = TelegramDispatcher(bot_token="simulated_token")

    # Critical heatwave meteorological parameters (Delhi peak conditions)
    weather_scenario = {
        "scenario_name": "Delhi Severe Heatwave Peak (June 2024 Analog)",
        "temperature_c": 44.5,
        "relative_humidity_pct": 45.0,
        "wind_speed_ms": 1.8,
        "solar_radiation_w_m2": 820.0,
        "consecutive_extreme_days": 3
    }

    print("\n🌡️ [METEOROLOGICAL FORCING]")
    print(f"  • Ambient Air Temp: {weather_scenario['temperature_c']}°C")
    print(f"  • Relative Humidity: {weather_scenario['relative_humidity_pct']}%")
    print(f"  • Wind Speed: {weather_scenario['wind_speed_ms']} m/s | Solar Irradiance: {weather_scenario['solar_radiation_w_m2']} W/m²")
    print(f"  • Heatwave Persistence: {weather_scenario['consecutive_extreme_days']} consecutive days")

    # Target high vulnerability wards
    all_wards = hvi_engine.get_all_wards_hvi()
    print(f"\n📍 Scanning {len(all_wards)} Municipal Wards for Alert Threshold Breaches (Risk >= 55.0)...")

    high_risk_dispatches = []

    for ward in all_wards:
        w_id = ward["ward_id"]
        risk_res = risk_engine.calculate_risk(
            ward_id=w_id,
            temp_c=weather_scenario["temperature_c"],
            rh_pct=weather_scenario["relative_humidity_pct"],
            wind_speed_2m_ms=weather_scenario["wind_speed_ms"],
            solar_radiation_w_m2=weather_scenario["solar_radiation_w_m2"],
            consecutive_extreme_days=weather_scenario["consecutive_extreme_days"]
        )

        risk_score = risk_res["risk_score"]
        if risk_score >= 55.0:
            advisory = AdvisoryEngine.generate_advisories(risk_res)
            
            # Dispatch simulated Telegram alert
            broadcast_res = await dispatcher.broadcast_ward_alert(
                ward_name=risk_res["ward_name"],
                risk_score=risk_score,
                risk_band=risk_res["risk_band"],
                thermal_metrics=risk_res["thermal_metrics"],
                municipal_playbook=advisory["municipal_playbook"],
                occupational_schedule=advisory["occupational_schedule"],
                language="both"
            )
            high_risk_dispatches.append((risk_res, advisory, broadcast_res))

    print(f"\n✅ Identified {len(high_risk_dispatches)} Wards requiring Immediate Civic Broadcast.")

    # 2. Display detailed dispatch payload for top critical ward
    if high_risk_dispatches:
        top_risk_res, top_advisory, top_broadcast = high_risk_dispatches[0]
        print("\n" + "━" * 70)
        print(f"📢 SAMPLE TELEGRAM BROADCAST PAYLOAD — {top_risk_res['ward_name']} ({top_risk_res['ward_id']})")
        print("━" * 70)
        print(top_broadcast["bulletin_text"])
        print("━" * 70)

        print("\n⚡ [ACTIVE ADMINISTRATIVE ACTION TRIGGERS]:")
        for trig in top_advisory.get("action_triggers", []):
            print(f"  ▶ [TRIGGER] {trig}")

        print("\n👷 [NIOSH OCCUPATIONAL ADVISORY ASSESSMENT]:")
        occ = AdvisoryEngine.get_occupational_advisory(
            temp_c=weather_scenario["temperature_c"],
            rh_pct=weather_scenario["relative_humidity_pct"],
            wind_speed_ms=weather_scenario["wind_speed_ms"],
            solar_radiation_w_m2=weather_scenario["solar_radiation_w_m2"],
            workload="heavy",
            sector="construction"
        )
        print(f"  • Work/Rest Schedule: {occ['niosh_schedule']['work_rest_ratio']}")
        print(f"  • Mandatory Work Stoppage: {occ['niosh_schedule']['work_stoppage_mandated']}")
        print(f"  • Hourly Fluid Quota: {occ['niosh_schedule']['hourly_hydration_liters']} L/hour ({occ['niosh_schedule']['hydration_frequency']})")
        print(f"  • Sector Directives (Construction):")
        for p in occ["sector_advisories"]["construction"]["protocols"]:
            print(f"    - {p}")

    print("\n" + "=" * 70)
    print("🎯 BROADCAST VERIFICATION COMPLETE: ALL DIRECTIVES FORMATTED & DISPATCHED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_dispatch_simulation())
