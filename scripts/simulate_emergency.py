#!/usr/bin/env python3
"""TrailSafe Autonomous Dead-Man Switch & TabPFN Risk Simulation.

Demonstrates the complete end-to-end solo hiker safety loop:
1. Trailhead initiation & baseline in-context TabPFN fit
2. Waypoint check-in with physiological Bayesian risk updates
3. Simulated hiker distress / missed checkpoint in cellular dead zone
4. Grace period acoustic alarm countdown
5. Temporal emergency escalation & multi-channel dispatch
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ml.tabpfn_engine import HikerTelemetry, TabPFNRiskEngine
from src.dispatch.notifier import EmergencyDispatchMessage, EmergencyDispatcher


def print_banner():
    print("\n" + "=" * 74)
    print(" 🏔️  TRAILSAFE: BACKCOUNTRY DEAD-MAN'S SWITCH SIMULATION")
    print(" Prior Labs TabPFN In-Context Bayesian Engine + Temporal Durable Execution")
    print("=" * 74)


def print_section(title: str):
    print(f"\n\033[1;36m▶ {title}\033[0m")
    print("-" * 60)


def format_risk_bar(prob: float) -> str:
    filled = int(prob * 30)
    empty = 30 - filled
    color = "\033[1;32m" if prob < 0.3 else "\033[1;33m" if prob < 0.6 else "\033[1;31m"
    return f"{color}[{'█' * filled}{'░' * empty}]\033[0m {prob * 100:.1f}%"


def simulate_countdown(seconds: int, prefix: str):
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        sys.stdout.write(f"\r  ⏱️  {prefix}: \033[1;33m{mins:02d}:{secs:02d}\033[0m remaining...")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write(f"\r  ⏱️  {prefix}: \033[1;31m00:00 [DEADLINE EXPIRED]\033[0m\n")
    sys.stdout.flush()


def run_simulation():
    print_banner()

    # Step 1: Initialization
    print_section("STEP 1: TRAILHEAD REGISTRATION & TABPFN IN-CONTEXT PRIORS")
    print("  Hiker:           Sanjay (Solo Mountaineer)")
    print("  Trail:           Netravali Ridge Trail (Western Ghats, Goa)")
    print("  Waypoints:       3 checkpoints (Gate -> Canyon -> Ridge Peak)")
    print("  Leg Timeout:     45 minutes per checkpoint")
    print("  Grace Period:    10 minutes with acoustic alarm")
    print("  Emergency Alert: +91 98230 XXXXX (Family) & Basecamp Rescue")
    
    print("\n  Loading Prior Labs TabPFN Foundation Model & historical trail priors...")
    t0 = time.time()
    engine = TabPFNRiskEngine.get_instance()
    t_load = time.time() - t0
    print(f"  ✓ TabPFN loaded and fitted in-context in \033[1;32m{t_load:.2f}s\033[0m (Zero training loops).")

    # Step 2: Checkpoint 1 (Normal)
    print_section("STEP 2: CHECKPOINT 1 — RIVER CANYON CROSSING (Screen-Zero Tap)")
    print("  Hiker reaches Checkpoint 1 on time. Phone stays zipped in pack.")
    print("  Hiker gives single tap on lock screen or scans NFC/QR waypoint post.")
    
    cp1_telem = HikerTelemetry(
        elevation_delta_m=120.0,
        pace_min_per_km=11.5,
        hours_elapsed=0.8,
        ambient_temp_c=25.5,
        water_remaining_ml=1800.0,
        cadence_spm=118.0,
        terrain_roughness_idx=1.4,
    )
    print(f"  Telemetry: Elevation +{cp1_telem.elevation_delta_m}m | Pace {cp1_telem.pace_min_per_km} min/km | Temp {cp1_telem.ambient_temp_c}°C | Water {cp1_telem.water_remaining_ml} mL")
    
    risk1 = engine.evaluate(cp1_telem)
    print(f"  TabPFN Bayesian Hazard Risk: {format_risk_bar(risk1.hazard_probability)}")
    print(f"  Projected Fluid Deficit:    \033[1;32m{risk1.projected_water_deficit_ml} mL\033[0m")
    print(f"  Status:                     \033[1;32mNOMINAL\033[0m — {risk1.recommendation}")
    print("  Temporal Durable Timer:     Window reset to 45:00 for Leg 2.")

    # Step 3: Checkpoint 2 (High Fatigue & Dehydration)
    print_section("STEP 3: CHECKPOINT 2 — STEEP SCRAMBLE (Elevated Risk Detected)")
    print("  Temperature spikes to 33.5°C; hiker climbs steep boulder field.")
    print("  Hiker taps checkpoint 2 check-in:")

    cp2_telem = HikerTelemetry(
        elevation_delta_m=340.0,
        pace_min_per_km=18.5,
        hours_elapsed=2.4,
        ambient_temp_c=33.5,
        water_remaining_ml=300.0,
        cadence_spm=88.0,
        terrain_roughness_idx=3.6,
    )
    print(f"  Telemetry: Elevation +{cp2_telem.elevation_delta_m}m | Pace {cp2_telem.pace_min_per_km} min/km | Temp {cp2_telem.ambient_temp_c}°C | Water {cp2_telem.water_remaining_ml} mL")
    
    risk2 = engine.evaluate(cp2_telem)
    print(f"  TabPFN Bayesian Hazard Risk: {format_risk_bar(risk2.hazard_probability)}")
    print(f"  Projected Fluid Deficit:    \033[1;33m{risk2.projected_water_deficit_ml} mL\033[0m")
    print(f"  Status:                     \033[1;33mELEVATED FATIGUE\033[0m — {risk2.recommendation}")
    print("  Temporal Durable Timer:     Window reset to 45:00 for Leg 3.")

    # Step 4: The Worst Case (Cellular Dead Zone + Hiker Down)
    print_section("STEP 4: LEG 3 TO RIDGE CREST — CELLULAR DEAD ZONE (No Service)")
    print("  Hiker enters dense canopy ravine. Cellular bars drop from 2G to \033[1;31mNO SERVICE\033[0m.")
    print("  Hiker trips on wet basalt, sustains ankle fracture, and cannot move.")
    print("  Hiker cannot reach Checkpoint 3.")
    
    print("\n  Temporal durable timer running on device / edge worker:")
    simulate_countdown(5, "Leg 3 Checkpoint Window")

    # Step 5: Grace Period
    print_section("STEP 5: DEAD-MAN SWITCH TIMEOUT — 10-MINUTE GRACE PERIOD")
    print("  Checkpoint window elapsed with zero hiker signal!")
    print("  State Transition: ACTIVE -> \033[1;33mGRACE_PERIOD\033[0m")
    print("  Action: Phone triggers high-decibel tactical acoustic siren (880Hz-1200Hz sweep).")
    print("  If hiker is safe, they can dismiss the alarm. Waiting for dismiss signal...")
    
    simulate_countdown(4, "Grace Period Siren Countdown")

    # Step 6: Emergency Escalation
    print_section("STEP 6: TEMPORAL EMERGENCY ESCALATION & RESCUE DISPATCH")
    print("  \033[1;31m🚨 GRACE PERIOD EXPIRED WITHOUT SIGNAL — DEAD-MAN SWITCH TRIGGERED!\033[0m")
    print("  Temporal executes durable activity: dispatch_emergency_alert_activity")

    dispatcher = EmergencyDispatcher()
    dispatch_msg = EmergencyDispatchMessage(
        hiker_id="Sanjay (Solo Mountaineer)",
        trail_name="Netravali Ridge Trail",
        last_checkpoint_id="cp-2",
        last_checkpoint_name="Checkpoint 2: Mid-Ridge Scramble",
        latitude=15.08920,
        longitude=74.21540,
        hours_elapsed=2.4,
        hazard_probability=risk2.hazard_probability,
        water_remaining_ml=cp2_telem.water_remaining_ml,
        timestamp=datetime.now(timezone.utc).isoformat(),
        reason="Missed Ridge Crest checkpoint beyond 45m window and 10m grace period. Probable injury in ravine.",
    )

    audit = dispatcher.dispatch(dispatch_msg)

    print("\n  Generated Rescue Payload Transmitted across Multi-Channel Gateways:")
    print("  " + "-" * 56)
    alert_text = dispatcher.format_alert_text(dispatch_msg)
    for line in alert_text.split("\n"):
        print(f"  | {line}")
    print("  " + "-" * 56)

    for ch in audit["channels"]:
        ch_name = ch.get("channel", "unknown").replace("_", " ").title()
        ch_status = ch.get("status", "unknown").upper()
        color = "\033[1;32m" if ch_status == "DELIVERED" else "\033[1;33m"
        print(f"  ✓ {ch_name} Status: {color}{ch_status}\033[0m")
    print(f"  ✓ Live Maps Pin:            \033[1;34mhttps://www.google.com/maps?q={dispatch_msg.latitude:.5f},{dispatch_msg.longitude:.5f}\033[0m")

    print("\n" + "=" * 74)
    print(" \033[1;32mSIMULATION COMPLETE: HIKER LOCATED & RESCUE PROTOCOL ACTIVATED.\033[0m")
    print(" TrailSafe protected the solo hiker even with zero bars of cell reception.")
    print("=" * 74 + "\n")


if __name__ == "__main__":
    run_simulation()
