#!/usr/bin/env python3
"""
CLI Utility: Historical Heatwave Hindcast Replay & 72h-120h Lead-Time Validation.
Demonstrates physiological thermal stress progression and multi-day early warning lead times.

Usage:
  python scripts/hindcast_replay.py
  python scripts/hindcast_replay.py --event delhi_june_2024 --ward DEL-W01
  python scripts/hindcast_replay.py --all
"""
import sys
import os
import argparse
import json

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.data_sources.hindcast_engine import HindcastEngine


def print_banner():
    print("=" * 80)
    print(" 🕒 HISTORICAL HEATWAVE HINDCAST REPLAY & 72h-120h LEAD-TIME ENGINE")
    print(" SIH26083 Human Thermal Risk & Public Health Early Warning System")
    print("=" * 80)


def display_event_replay(result: dict):
    print(f"\n📍 EVENT: {result['event_name']}")
    print(f"   Region: {result['city']}, {result['state']} | Date Range: {result['date_range']}")
    print(f"   Target Ward: {result['target_ward']['ward_name']} ({result['target_ward']['ward_id']}) - HVI: {result['target_ward']['hvi_score']}/100")
    print(f"   Epidemiological Grounding: {result['lead_time_proof']['epidemiological_validation']['benchmark_study']}")
    print("-" * 80)
    print(f"{'Horizon':<6} | {'Lead':<6} | {'Date':<10} | {'T2M':<6} | {'RH%':<5} | {'UTCI':<7} | {'WBGT':<7} | {'Risk':<10} | {'Early Action / Advisory'}")
    print("-" * 80)

    for step in result["timeline_progression"]:
        hor = step["horizon"]
        lead = f"{step['lead_time_hours']}h"
        dt = step["date"]
        t = f"{step['meteorology']['temperature_c']}°C"
        rh = f"{step['meteorology']['relative_humidity_pct']}%"
        utci = f"{step['physiological_indices']['utci_c']}°C"
        wbgt = f"{step['physiological_indices']['wbgt_c']}°C"
        risk = f"{step['risk_assessment']['risk_score']} ({step['risk_assessment']['risk_band'][:4]})"
        rationale = step["lead_time_comparison"]["early_action_rationale"]
        
        # Truncate rationale if needed for neat table display
        if len(rationale) > 42:
            short_rationale = rationale[:39] + "..."
        else:
            short_rationale = rationale

        print(f"{hor:<6} | {lead:<6} | {dt:<10} | {t:<6} | {rh:<5} | {utci:<7} | {wbgt:<7} | {risk:<10} | {short_rationale}")

    print("-" * 80)
    proof = result["lead_time_proof"]
    summary = result["summary_metrics"]
    print(f"🎯 LEAD-TIME PROOF SUMMARY:")
    print(f"   • Early Warning Triggered At:       {proof['early_warning_lead_hours']}h lead time (D-5 / D-4)")
    print(f"   • High-Risk Emergency Alert At:     {proof['elevated_high_risk_lead_hours']}h lead time (D-3 / 72h in advance)")
    print(f"   • Peak Thermal Crisis on D-Day:     UTCI {summary['peak_utci_c']}°C | WBGT {summary['peak_wbgt_c']}°C | Composite Risk {summary['peak_risk_score']}/100")
    print(f"   • Outcome:                          Proactive civic pre-deployment (cooling centers, ORS surges, labour shifts)")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Historical Heatwave Hindcast Replay")
    parser.add_argument("--event", type=str, default="delhi_june_2024", help="Event ID (e.g., delhi_june_2024, ahmedabad_may_2010, delhi_may_2022)")
    parser.add_argument("--ward", type=str, default="DEL-W01", help="Ward ID (default: DEL-W01 Seelampur)")
    parser.add_argument("--all", action="store_true", help="Replay all historical benchmark events")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of table")

    args = parser.parse_args()
    engine = HindcastEngine()

    if args.json:
        if args.all:
            events = engine.get_events_catalog()
            outputs = [engine.replay_event(e["event_id"], ward_id=args.ward) for e in events]
            print(json.dumps(outputs, indent=2))
        else:
            res = engine.replay_event(args.event, ward_id=args.ward)
            print(json.dumps(res, indent=2))
        return

    print_banner()

    if args.all:
        catalog = engine.get_events_catalog()
        for ev in catalog:
            res = engine.replay_event(ev["event_id"], ward_id=args.ward)
            display_event_replay(res)
    else:
        res = engine.replay_event(args.event, ward_id=args.ward)
        display_event_replay(res)


if __name__ == "__main__":
    main()
