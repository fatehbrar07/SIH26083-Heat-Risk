import pytest
import asyncio
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.advisory.advisory_engine import AdvisoryEngine
from backend.app.advisory.telegram_dispatcher import TelegramDispatcher
from backend.app.models.schemas import AlertBroadcastRequest

client = TestClient(app)

# 1. Telegram Dispatcher Unit Tests

def test_telegram_html_bulletin_formatting():
    dispatcher = TelegramDispatcher(bot_token="simulated_token")
    html = dispatcher.format_html_bulletin(
        ward_name="Chandni Chowk",
        risk_score=85.2,
        risk_band="Very High Risk",
        thermal_metrics={"utci_c": 46.5, "wbgt_c": 33.1, "heat_index_c": 52.0},
        municipal_playbook={
            "english": ["Activate emergency cooling centers", "Deploy water tankers"],
            "hindi": ["आपातकालीन शीतलन केंद्र सक्रिय करें", "पानी के टैंकर तैनात करें"]
        },
        occupational_schedule="Halt unconditioned outdoor manual labor (0% Work / 100% Rest)",
        language="both"
    )

    assert "Chandni Chowk" in html
    assert "85.2" in html
    assert "46.5°C" in html
    assert "33.1°C" in html
    assert "Activate emergency cooling centers" in html
    assert "आपातकालीन शीतलन केंद्र" in html
    assert "Halt unconditioned outdoor manual labor" in html

def test_telegram_markdown_bulletin_formatting():
    dispatcher = TelegramDispatcher()
    md = dispatcher.format_markdown_bulletin(
        ward_name="Okhla Industrial Area",
        risk_score=72.0,
        risk_band="High Risk",
        thermal_metrics={"utci_c": 41.0, "wbgt_c": 30.5},
        occupational_schedule="25% Work / 75% Rest per hour"
    )

    assert "Okhla Industrial Area" in md
    assert "72.0/100" in md
    assert "41.0°C" in md
    assert "25% Work / 75% Rest" in md

@pytest.mark.asyncio
async def test_telegram_simulated_dispatch():
    dispatcher = TelegramDispatcher(bot_token="", chat_id="")
    res = await dispatcher.send_message("Test Alert Message", chat_id="@simulated_channel")
    assert res["status"] == "simulated"
    assert res["delivered"] is True
    assert "Test Alert Message" in res["message_preview"]

@pytest.mark.asyncio
async def test_telegram_broadcast_ward_alert():
    dispatcher = TelegramDispatcher(bot_token="simulated_token")
    result = await dispatcher.broadcast_ward_alert(
        ward_name="Seelampur",
        risk_score=88.0,
        risk_band="Very High Risk",
        thermal_metrics={"utci_c": 47.0, "wbgt_c": 33.5, "heat_index_c": 54.0},
        municipal_playbook={"english": ["Deploy tankers"], "hindi": ["टैंकर तैनात करें"]},
        occupational_schedule="Halt unconditioned outdoor manual labor",
        language="both"
    )

    assert result["ward_name"] == "Seelampur"
    assert result["risk_score"] == 88.0
    assert result["dispatch"]["delivered"] is True
    assert "Seelampur" in result["bulletin_text"]

# 2. Advisory Engine Unit Tests

def test_advisory_engine_critical_triggers():
    critical_data = {
        "ward_name": "Sadar Bazar",
        "risk_score": 86.5,
        "risk_band": "Very High Risk",
        "thermal_metrics": {"wbgt_c": 33.0, "utci_c": 47.2}
    }
    adv = AdvisoryEngine.generate_advisories(critical_data)
    assert "ACTIVATE_COOLING_CENTERS" in adv["action_triggers"]
    assert "DEPLOY_WATER_TANKERS_INFORMAL_SETTLEMENTS" in adv["action_triggers"]
    assert "HALT_OUTDOOR_LABOR_11_TO_16" in adv["action_triggers"]
    assert "HOSPITAL_SURGE_BED_ACTIVATION" in adv["action_triggers"]
    assert len(adv["municipal_playbook"]["english"]) >= 3
    assert len(adv["municipal_playbook"]["hindi"]) >= 3

def test_advisory_engine_moderate_triggers():
    mod_data = {
        "ward_name": "Vasant Vihar",
        "risk_score": 42.0,
        "risk_band": "Moderate Risk",
        "thermal_metrics": {"wbgt_c": 27.5, "utci_c": 34.0}
    }
    adv = AdvisoryEngine.generate_advisories(mod_data)
    assert "STANDARD_HEAT_ADVISORY" in adv["action_triggers"]

def test_occupational_niosh_heavy_workload_halt():
    # Extreme conditions: 44°C, 50% RH -> WBGT > 34°C
    occ = AdvisoryEngine.get_occupational_advisory(
        temp_c=44.0,
        rh_pct=50.0,
        wind_speed_ms=1.5,
        solar_radiation_w_m2=800.0,
        workload="heavy",
        acclimatized=True
    )
    assert occ["niosh_schedule"]["work_stoppage_mandated"] is True
    assert occ["niosh_schedule"]["work_minutes_per_hour"] == 0
    assert occ["niosh_schedule"]["hourly_hydration_liters"] >= 1.25
    assert occ["niosh_schedule"]["electrolyte_recommended"] is True

def test_occupational_niosh_acclimatization_difference():
    # Moderate conditions where acclimatized can work continuous, but unacclimatized needs rest
    wbgt_test = 27.0
    occ_acclimatized = AdvisoryEngine.get_occupational_advisory(
        wbgt_c=wbgt_test,
        workload="moderate",
        acclimatized=True
    )
    occ_unacclimatized = AdvisoryEngine.get_occupational_advisory(
        wbgt_c=wbgt_test,
        workload="moderate",
        acclimatized=False
    )
    # Acclimatized allows continuous work at 27.0°C (threshold is 28.0°C)
    assert occ_acclimatized["niosh_schedule"]["work_minutes_per_hour"] == 60
    # Unacclimatized requires rest breaks at 27.0°C (threshold is 25.7°C)
    assert occ_unacclimatized["niosh_schedule"]["work_minutes_per_hour"] < 60

def test_occupational_sector_advisories():
    occ_gig = AdvisoryEngine.get_occupational_advisory(
        temp_c=41.0,
        rh_pct=40.0,
        sector="gig_delivery"
    )
    assert "gig_delivery" in occ_gig["sector_advisories"]
    assert "Dark Store Cooling Hubs" in "".join(occ_gig["sector_advisories"]["gig_delivery"]["protocols"])

    occ_construction = AdvisoryEngine.get_occupational_advisory(
        temp_c=41.0,
        rh_pct=40.0,
        sector="construction"
    )
    assert "construction" in occ_construction["sector_advisories"]
    assert "Split Shift Mandate" in "".join(occ_construction["sector_advisories"]["construction"]["protocols"])

# 3. API Integration Tests

def test_api_advisory_occupational_endpoint():
    res = client.get("/api/v1/advisory/occupational?temp_c=42.0&rh_pct=40.0&workload=heavy&sector=construction")
    assert res.status_code == 200
    data = res.json()
    assert "thermal_inputs" in data
    assert "niosh_schedule" in data
    assert "sector_advisories" in data
    assert "heat_illness_protocols" in data
    assert data["niosh_schedule"]["hourly_hydration_liters"] > 0

def test_api_alerts_broadcast_single_ward():
    payload = {
        "ward_id": "DEL-W01",
        "temperature_c": 44.0,
        "relative_humidity_pct": 45.0,
        "wind_speed_ms": 2.0,
        "solar_radiation_w_m2": 750.0,
        "consecutive_extreme_days": 2,
        "simulate": True,
        "language": "both"
    }
    res = client.post("/api/v1/alerts/broadcast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "broadcast_id" in data
    assert data["status"] == "simulated"
    assert data["target_wards_count"] == 1
    assert len(data["dispatched_alerts"]) == 1
    alert = data["dispatched_alerts"][0]
    assert alert["ward_id"] == "DEL-W01"
    assert "bulletin_html" in alert
    assert "action_triggers" in alert
    assert len(data["summary_action_triggers"]) > 0

def test_api_alerts_broadcast_multi_ward_threshold():
    payload = {
        "min_risk_threshold": 60.0,
        "temperature_c": 45.0,
        "relative_humidity_pct": 50.0,
        "wind_speed_ms": 1.5,
        "solar_radiation_w_m2": 800.0,
        "consecutive_extreme_days": 3,
        "simulate": True
    }
    res = client.post("/api/v1/alerts/broadcast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "simulated"
    assert data["target_wards_count"] > 0
    for dispatched in data["dispatched_alerts"]:
        assert dispatched["risk_score"] >= 60.0
