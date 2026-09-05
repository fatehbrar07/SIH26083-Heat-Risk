#!/usr/bin/env python3
"""
CLI Utility to test the scientific thermal stress engines (UTCI, WBGT, Heat Index)
across contrasting microclimatic regimes.
"""
import sys
from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.thermal.heat_index_engine import HeatIndexEngine

def test_scenario(name: str, temp: float, rh: float, wind: float, solar: float):
    print(f"\n--- {name} ---")
    print(f"Inputs: Air Temp = {temp}°C | RH = {rh}% | Wind = {wind} m/s | Solar = {solar} W/m²")
    
    utci = UTCIEngine.calculate_utci(temp, rh, wind, solar)
    utci_cat = UTCIEngine.get_utci_category(utci)
    
    wbgt = WBGTEngine.calculate_outdoor_wbgt(temp, rh, wind, solar)
    wbgt_adv = WBGTEngine.get_occupational_advisory(wbgt)
    
    hi = HeatIndexEngine.calculate_heat_index(temp, rh)
    hi_cat = HeatIndexEngine.get_heat_index_category(hi)
    
    print(f"  • UTCI:        {utci}°C  -->  {utci_cat['category']}")
    print(f"  • WBGT:        {wbgt}°C  -->  {wbgt_adv['category']} | Work Schedule: {wbgt_adv['work_rest_cycle']}")
    print(f"  • Heat Index:  {hi}°C    -->  {hi_cat['category']}")

def main():
    print("================================================================")
    print("🌡️  SIH26083 SCIENTIFIC THERMAL STRESS ENGINE BENCHMARK")
    print("================================================================")
    
    # Scenario 1: Dry Heat (North-West Desert Wind)
    test_scenario("Scenario A: Dry Heat (Desert Flow)", temp=40.0, rh=20.0, wind=3.5, solar=650.0)
    
    # Scenario 2: Lethal Humid Heat (Monsoon Transition)
    test_scenario("Scenario B: Lethal Humid Heat (Monsoon Surge)", temp=40.0, rh=70.0, wind=1.0, solar=650.0)
    
    # Scenario 3: Extreme Delhi Summer Spike (June 2024 Replay)
    test_scenario("Scenario C: Extreme Delhi Spike (June 2024)", temp=44.5, rh=42.0, wind=2.2, solar=820.0)
    
    print("\n✅ Scientific benchmark demonstrates why air temperature alone is misleading.")

if __name__ == "__main__":
    main()
