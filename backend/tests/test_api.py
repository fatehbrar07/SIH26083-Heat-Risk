import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "tier_1_sources" in data

def test_locations_endpoint():
    res = client.get("/api/v1/locations")
    assert res.status_code == 200
    data = res.json()
    assert "wards" in data
    assert len(data["wards"]) > 0

def test_thermal_current_endpoint():
    res = client.get("/api/v1/thermal/current?temp_c=40.0&rh_pct=35.0&wind_speed_ms=2.5&solar_radiation_w_m2=650.0")
    assert res.status_code == 200
    data = res.json()
    assert "utci" in data
    assert "wbgt" in data
    assert "heat_index" in data
    assert data["utci"]["value_c"] > 0

def test_risk_current_endpoint():
    res = client.get("/api/v1/risk/current?ward_id=DEL-W01&temp_c=40.0&rh_pct=35.0")
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "risk_band" in data
    assert "disclaimer" in data

def test_map_risk_geojson():
    res = client.get("/api/v1/map/risk?temp_c=40.0&rh_pct=35.0")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    assert "risk_score" in data["features"][0]["properties"]

def test_advisory_bilingual():
    res = client.get("/api/v1/advisory?ward_id=DEL-W01&temp_c=42.0&rh_pct=50.0")
    assert res.status_code == 200
    data = res.json()
    assert "municipal_playbook" in data
    assert "english" in data["municipal_playbook"]
    assert "hindi" in data["municipal_playbook"]
