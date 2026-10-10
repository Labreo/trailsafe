"""Interactive Rich Field CLI for TrailSafe Solo Hiker Safety.

Provides a tactical terminal interface for initiating trail sessions,
tracking dead-man switch countdowns, and transmitting checkpoint signals.
"""

import argparse
import asyncio
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from temporalio.client import Client

from src.config import settings
from src.temporal.worker import create_temporal_client
from src.temporal.workflows import TrailSafetyWorkflow, TrailSessionParams

console = Console()


def load_trail_checkpoints(trail_identifier: str) -> Dict[str, Any]:
    """Loads matching trail configuration from data/test_checkpoints.json."""
    checkpoints_file = settings.DATA_DIR / "test_checkpoints.json"
    if not checkpoints_file.exists():
        console.print(f"[red]Checkpoints file not found: {checkpoints_file}[/red]")
        sys.exit(1)

    with open(checkpoints_file, "r", encoding="utf-8") as f:
        trails: List[Dict[str, Any]] = json.load(f)

    for trail in trails:
        if (
            trail["trail_id"].lower() == trail_identifier.lower()
            or trail_identifier.lower() in trail["trail_name"].lower()
        ):
            return trail

    # Default fallback to first trail
    return trails[0]


async def run_field_session(
    trail_identifier: str,
    timeout_minutes: int,
    hiker_name: str,
) -> None:
    """Manages live field CLI session against Temporal cluster."""
    trail_data = load_trail_checkpoints(trail_identifier)
    checkpoints = trail_data["checkpoints"]

    console.print(
        Panel(
            f"[bold green]TrailSafe Tactical Field Monitor[/bold green]\n"
            f"Hiker: [white]{hiker_name}[/white]\n"
            f"Trail: [cyan]{trail_data['trail_name']}[/cyan] ({trail_data['location']})\n"
            f"Distance: [yellow]{trail_data['total_distance_km']} km[/yellow] | "
            f"Elevation Gain: [yellow]+{trail_data['elevation_gain_m']} m[/yellow]\n"
            f"Checkpoint Timeout: [white]{timeout_minutes} minutes[/white]",
            title="Session Initialization",
            border_style="green",
        )
    )

    try:
        client = await create_temporal_client()
    except Exception as e:
        console.print(f"[bold red]Cannot connect to Temporal cluster ({settings.TEMPORAL_TARGET_HOST}): {e}[/bold red]")
        console.print("[yellow]Start the local Temporal server with: temporal server start-dev[/yellow]")
        return

    workflow_id = f"trailsafe-{trail_data['trail_id']}-{int(time.time())}"
    console.print(f"Connecting to Temporal workflow: [cyan]{workflow_id}[/cyan]...")

    params = {
        "hiker_id": hiker_name,
        "trail_id": trail_data["trail_id"],
        "trail_name": trail_data["trail_name"],
        "checkpoints": checkpoints,
        "checkpoint_timeout_seconds": timeout_minutes * 60,
        "grace_period_seconds": settings.SAFETY_GRACE_PERIOD_MINUTES * 60,
        "initial_telemetry": {
            "elevation_delta_m": 0.0,
            "pace_min_per_km": checkpoints[0].get("expected_pace_min_per_km", 11.0),
            "hours_elapsed": 0.1,
            "ambient_temp_c": 24.0,
            "water_remaining_ml": 2000.0,
            "cadence_spm": 120.0,
            "terrain_roughness_idx": checkpoints[0].get("terrain_roughness_idx", 1.1),
        },
    }

    handle = await client.start_workflow(
        TrailSafetyWorkflow.run,
        params,
        id=workflow_id,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
    )
    console.print("[bold green]Workflow launched successfully. Dead-man switch active.[/bold green]")

    while True:
        try:
            status: Dict[str, Any] = await handle.query(TrailSafetyWorkflow.get_hiker_status)
        except Exception as q_err:
            console.print(f"[yellow]Status query pending: {q_err}[/yellow]")
            status = {}

        # Render tactical status table
        table = Table(title=f"Trail Status: {trail_data['trail_name']}", border_style="blue")
        table.add_column("Property", style="dim")
        table.add_column("Value", style="bold")

        curr_idx = status.get("current_checkpoint_idx", 0)
        curr_cp = status.get("current_checkpoint", {}) or {}
        risk = status.get("latest_risk", {}) or {}

        table.add_row("Workflow ID", workflow_id)
        table.add_row("Execution State", f"[{'green' if status.get('status') == 'ACTIVE' else 'red'}]{status.get('status', 'ACTIVE')}[/]")
        table.add_row("Active Waypoint", f"{curr_cp.get('name', 'N/A')} (Leg {curr_idx + 1} of {len(checkpoints)})")
        table.add_row("Waypoint Elevation", f"{curr_cp.get('elevation_m', 0)} m")

        hazard_prob = risk.get("hazard_probability", 0.0)
        risk_color = "red" if hazard_prob >= 0.70 else ("yellow" if hazard_prob >= 0.40 else "green")
        table.add_row("TabPFN Bayesian Hazard Risk", f"[{risk_color}]{hazard_prob * 100:.1f}%[/]")
        table.add_row("Water Shortfall Forecast", f"{risk.get('projected_water_deficit_ml', 0.0)} mL")
        table.add_row("Field Recommendation", risk.get("recommendation", "Proceed nominal."))

        console.print(table)

        if status.get("status") in ("COMPLETED", "EMERGENCY_DISPATCHED", "CANCELLED"):
            console.print(f"[bold red]Session ended with status: {status.get('status')}[/bold red]")
            break

        console.print("[bold]Tactical Actions:[/bold]")
        console.print("  [C] Transmit Check-in Signal")
        console.print("  [E] Extend Window (15 mins)")
        console.print("  [S] Emergency SOS Panic Button")
        console.print("  [F] Finish Trail Leg")
        console.print("  [Q] Exit Monitor")

        action = Prompt.ask("Select command", choices=["c", "e", "s", "f", "q"], default="c")

        if action.lower() == "c":
            elev_delta = float(curr_cp.get("elevation_m", 150) - 90)
            telemetry = {
                "elevation_delta_m": elev_delta,
                "pace_min_per_km": float(curr_cp.get("expected_pace_min_per_km", 13.0)),
                "hours_elapsed": round(0.5 + curr_idx * 0.8, 1),
                "ambient_temp_c": 28.5,
                "water_remaining_ml": max(100.0, 2000.0 - (curr_idx * 400.0)),
                "cadence_spm": 110.0,
                "terrain_roughness_idx": float(curr_cp.get("terrain_roughness_idx", 2.0)),
            }
            signal_payload = {
                "checkpoint_id": curr_cp.get("id", f"cp-{curr_idx + 1}"),
                "telemetry": telemetry,
            }
            await handle.signal(TrailSafetyWorkflow.check_in, signal_payload)
            console.print("[green]Check-in signal transmitted to Temporal workflow.[/green]")
            await asyncio.sleep(2)

        elif action.lower() == "e":
            await handle.signal(TrailSafetyWorkflow.extend_window, 15)
            console.print("[yellow]Window extended by 15 minutes.[/yellow]")
            await asyncio.sleep(1)

        elif action.lower() == "s":
            reason = Prompt.ask("Enter emergency reason", default="Severe injury or terrain entrapment")
            await handle.signal(TrailSafetyWorkflow.emergency_sos, reason)
            console.print("[bold red]EMERGENCY SOS SIGNAL TRANSMITTED.[/bold red]")
            await asyncio.sleep(2)

        elif action.lower() == "f":
            await handle.signal(TrailSafetyWorkflow.complete_hike)
            console.print("[bold green]Hike marked complete.[/bold green]")
            break

        elif action.lower() == "q":
            console.print("Exiting CLI monitor. Workflow continues durably on Temporal cluster.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="TrailSafe Field CLI")
    parser.add_argument("--trail", default="Netravali Ridge", help="Trail name or identifier")
    parser.add_argument("--timeout", type=int, default=15, help="Checkpoint timeout in minutes")
    parser.add_argument("--hiker", default="Solo Explorer", help="Hiker name")
    args = parser.parse_args()

    asyncio.run(run_field_session(args.trail, args.timeout, args.hiker))


if __name__ == "__main__":
    main()
