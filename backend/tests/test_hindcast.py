import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.data_sources.hindcast_engine import HindcastEngine

client = TestClient(app)

def test_hindcast_catalog():
    engine = HindcastEngine()
    catalog = engine.get_events_catalog()
    assert len(catalog) == 3
    event_ids = {e["event_id"] for e in catalog}
    assert "delhi_june_2024" in event_ids
    assert "ahmedabad_may_2010" in event_ids
    assert "delhi_may_2022" in event_ids

def test_hindcast_replay_delhi_2024():
    engine = HindcastEngine()
    result = engine.replay_event("delhi_june_2024", ward_id="DEL-W01")
    assert result["event_id"] == "delhi_june_2024"
    assert len(result["timeline_progression"]) == 6
    
    # Check D-5 and D-Day progression
    d5 = result["timeline_progression"][0]
    assert d5["horizon"] == "D-5"
    assert d5["lead_time_hours"] == 120
    assert d5["physiological_indices"]["utci_c"] > 45.0  # High stress due to humidity

    d_day = result["timeline_progression"][-1]
    assert d_day["horizon"] == "D-Day"
    assert d_day["lead_time_hours"] == 0
    assert d_day["risk_assessment"]["risk_score"] >= 80.0

    # Verify lead time proof
    proof = result["lead_time_proof"]
    assert proof["early_warning_lead_hours"] >= 96
    assert proof["elevated_high_risk_lead_hours"] >= 72

def test_hindcast_replay_ahmedabad_2010():
    engine = HindcastEngine()
    result = engine.replay_event("ahmedabad_may_2010", ward_id="DEL-W01")
    assert result["event_id"] == "ahmedabad_may_2010"
    assert result["summary_metrics"]["peak_temperature_c"] == 46.8
    assert len(result["timeline_progression"]) == 6
    assert "Azhar" in result["lead_time_proof"]["epidemiological_validation"]["citations"][0]

def test_hindcast_replay_delhi_2022():
    engine = HindcastEngine()
    result = engine.replay_event("delhi_may_2022", ward_id="DEL-W01")
    assert result["event_id"] == "delhi_may_2022"
    assert result["summary_metrics"]["peak_temperature_c"] == 45.8
    assert len(result["timeline_progression"]) == 6

def test_api_hindcast_events_endpoint():
    res = client.get("/api/v1/hindcast/events")
    assert res.status_code == 200
    data = res.json()
    assert "catalog" in data
    assert data["total_events"] == 3

def test_api_hindcast_replay_endpoint():
    res = client.get("/api/v1/hindcast/replay?event_id=delhi_june_2024&ward_id=DEL-W01")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == "delhi_june_2024"
    assert "timeline_progression" in data
    assert len(data["timeline_progression"]) == 6
    assert data["lead_time_proof"]["early_warning_lead_hours"] in [96, 120]

def test_api_hindcast_replay_404():
    res = client.get("/api/v1/hindcast/replay?event_id=non_existent_heatwave")
    assert res.status_code == 404
