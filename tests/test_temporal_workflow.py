"""Unit tests for Temporal TrailSafetyWorkflow and activities.

Uses Temporal's official in-memory time-skipping test server to verify
durable state transitions, signals, queries, and activities without mocking.
"""

import asyncio
from datetime import timedelta
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.temporal.workflows import TrailSafetyWorkflow
from src.temporal.activities import (
    evaluate_tabpfn_risk_activity,
    dispatch_emergency_alert_activity,
    log_trail_telemetry_activity,
)


@pytest.mark.asyncio
async def test_workflow_signal_check_in_and_query():
    """Verifies that check_in signals advance checkpoints and queries return state."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        task_queue = "test-queue"
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[TrailSafetyWorkflow],
            activities=[
                evaluate_tabpfn_risk_activity,
                dispatch_emergency_alert_activity,
                log_trail_telemetry_activity,
            ],
        ):
            params = {
                "hiker_id": "Test Hiker",
                "trail_id": "netravali-test",
                "trail_name": "Netravali Ridge",
                "checkpoints": [
                    {"id": "cp-1", "name": "Gate", "elevation_m": 90, "distance_km": 0.0},
                    {"id": "cp-2", "name": "Falls", "elevation_m": 240, "distance_km": 3.4},
                ],
                "checkpoint_timeout_seconds": 600,
                "grace_period_seconds": 120,
            }

            handle = await env.client.start_workflow(
                TrailSafetyWorkflow.run,
                params,
                id="test-hike-workflow-1",
                task_queue=task_queue,
            )

            # Query initial state
            status = await handle.query(TrailSafetyWorkflow.get_hiker_status)
            assert status["status"] == "ACTIVE"
            assert status["current_checkpoint_idx"] == 0
            assert status["total_checkpoints"] == 2

            # Signal Check-in
            telemetry = {
                "elevation_delta_m": 150.0,
                "pace_min_per_km": 12.0,
                "hours_elapsed": 0.8,
                "ambient_temp_c": 26.0,
                "water_remaining_ml": 1800.0,
                "cadence_spm": 115.0,
                "terrain_roughness_idx": 1.5,
            }
            await handle.signal(TrailSafetyWorkflow.check_in, {"checkpoint_id": "cp-1", "telemetry": telemetry})

            # Poll for check-in processing and background TabPFN risk activity
            status_after = None
            for _ in range(60):
                await asyncio.sleep(0.5)
                try:
                    status_after = await handle.query(TrailSafetyWorkflow.get_hiker_status)
                    if status_after.get("latest_risk") and "hazard_probability" in status_after["latest_risk"]:
                        break
                except Exception:
                    continue

            assert status_after is not None
            assert status_after["current_checkpoint_idx"] >= 1
            assert status_after["latest_risk"] != {}
            assert "hazard_probability" in status_after["latest_risk"]

            # Signal complete hike
            await handle.signal(TrailSafetyWorkflow.complete_hike)
            result = await handle.result()
            assert result["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_workflow_manual_sos_trigger():
    """Verifies that emergency_sos immediately halts and triggers dispatch."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        task_queue = "test-queue-sos"
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[TrailSafetyWorkflow],
            activities=[
                evaluate_tabpfn_risk_activity,
                dispatch_emergency_alert_activity,
                log_trail_telemetry_activity,
            ],
        ):
            params = {
                "hiker_id": "Distressed Hiker",
                "trail_id": "ridge-danger",
                "trail_name": "Danger Ridge",
                "checkpoints": [
                    {"id": "cp-1", "name": "Start", "elevation_m": 100, "distance_km": 0.0},
                    {"id": "cp-2", "name": "Cliff", "elevation_m": 500, "distance_km": 5.0},
                ],
                "checkpoint_timeout_seconds": 300,
                "grace_period_seconds": 60,
            }

            handle = await env.client.start_workflow(
                TrailSafetyWorkflow.run,
                params,
                id="test-hike-sos",
                task_queue=task_queue,
            )

            # Signal immediate panic SOS
            await handle.signal(TrailSafetyWorkflow.emergency_sos, "Fell into ravine with ankle fracture")
            result = await handle.result()

            assert result["status"] == "EMERGENCY_DISPATCHED"
            assert "ravine" in result["reason"]
            assert "dispatch_result" in result


@pytest.mark.asyncio
async def test_workflow_window_extension():
    """Verifies that hikers signaling window extensions push deadlines back durably."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        task_queue = "test-queue-extend"
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[TrailSafetyWorkflow],
            activities=[
                evaluate_tabpfn_risk_activity,
                dispatch_emergency_alert_activity,
                log_trail_telemetry_activity,
            ],
        ):
            params = {
                "hiker_id": "Resting Hiker",
                "trail_id": "netravali-ridge",
                "trail_name": "Netravali Ridge",
                "checkpoints": [
                    {"id": "cp-1", "name": "Trailhead", "elevation_m": 90, "distance_km": 0.0},
                    {"id": "cp-2", "name": "Overlook", "elevation_m": 350, "distance_km": 4.0},
                ],
                "checkpoint_timeout_seconds": 60,
                "grace_period_seconds": 15,
            }

            handle = await env.client.start_workflow(
                TrailSafetyWorkflow.run,
                params,
                id="test-hike-extend",
                task_queue=task_queue,
            )

            # Signal 15-minute rest extension
            await handle.signal(TrailSafetyWorkflow.extend_window, 15)
            status = await handle.query(TrailSafetyWorkflow.get_hiker_status)
            assert status["extended_seconds"] == 900

            # Safe completion
            await handle.signal(TrailSafetyWorkflow.complete_hike)
            result = await handle.result()
            assert result["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_workflow_dead_man_timeout_and_escalation():
    """Verifies that unattended timeout + grace period triggers automatic emergency escalation."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        task_queue = "test-queue-timeout"
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[TrailSafetyWorkflow],
            activities=[
                evaluate_tabpfn_risk_activity,
                dispatch_emergency_alert_activity,
                log_trail_telemetry_activity,
            ],
        ):
            params = {
                "hiker_id": "Lost Solo Explorer",
                "trail_id": "dudhsagar-trek",
                "trail_name": "Dudhsagar Jungle Path",
                "checkpoints": [
                    {"id": "cp-1", "name": "Railway Gate", "elevation_m": 120, "distance_km": 0.0},
                    {"id": "cp-2", "name": "Canyon Crossing", "elevation_m": 420, "distance_km": 6.5},
                ],
                "checkpoint_timeout_seconds": 5,
                "grace_period_seconds": 2,
            }

            handle = await env.client.start_workflow(
                TrailSafetyWorkflow.run,
                params,
                id="test-hike-timeout",
                task_queue=task_queue,
            )

            # Zero signals sent: time-skipping server fast-forwards through normal window + grace period
            result = await handle.result()
            assert result["status"] == "EMERGENCY_DISPATCHED"
            assert "timeout and grace period" in result["reason"]
            assert "dispatch_result" in result

