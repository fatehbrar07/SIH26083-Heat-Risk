import pytest
import math
from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.thermal.heat_index_engine import HeatIndexEngine
from backend.app.vulnerability.hvi_engine import HVIEngine
from backend.app.risk.risk_engine import RiskEngine

def test_utci_monotonic_humidity():
    """Verify that under constant 40°C air temperature, increasing humidity increases UTCI."""
    utci_low_rh = UTCIEngine.calculate_utci(temp_c=40.0, rh_pct=20.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=500.0)
    utci_high_rh = UTCIEngine.calculate_utci(temp_c=40.0, rh_pct=70.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=500.0)
    assert utci_high_rh > utci_low_rh
    assert utci_high_rh - utci_low_rh > 5.0  # Significant physiological elevation

def test_wbgt_monotonic_radiation():
    """Verify that outdoor solar radiation increases outdoor WBGT."""
    wbgt_shade = WBGTEngine.calculate_outdoor_wbgt(temp_c=38.0, rh_pct=40.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=0.0)
    wbgt_sun = WBGTEngine.calculate_outdoor_wbgt(temp_c=38.0, rh_pct=40.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=800.0)
    assert wbgt_sun > wbgt_shade

def test_heat_index_sanity():
    """Verify NOAA Heat Index sanity on warm humid condition."""
    hi_dry = HeatIndexEngine.calculate_heat_index(temp_c=35.0, rh_pct=20.0)
    hi_humid = HeatIndexEngine.calculate_heat_index(temp_c=35.0, rh_pct=75.0)
    assert hi_humid > hi_dry

def test_hvi_vulnerability_bounds():
    """Ensure HVI score stays strictly within 0 - 100."""
    engine = HVIEngine()
    wards = engine.get_all_wards_hvi()
    assert len(wards) > 0
    for w in wards:
        assert 0.0 <= w["hvi_score"] <= 100.0

def test_risk_engine_monotonicity():
    """Test that higher vulnerability produces strictly higher or equal risk under identical weather."""
    risk_eng = RiskEngine()
    # High vulnerability ward vs Low vulnerability ward
    risk_high_vuln = risk_eng.calculate_risk("DEL-W01", temp_c=42.0, rh_pct=40.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=700.0)
    risk_low_vuln = risk_eng.calculate_risk("DEL-W04", temp_c=42.0, rh_pct=40.0, wind_speed_2m_ms=2.0, solar_radiation_w_m2=700.0)
    
    assert risk_high_vuln["risk_score"] > risk_low_vuln["risk_score"]
    assert 0.0 <= risk_high_vuln["risk_score"] <= 100.0
