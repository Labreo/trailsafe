"""Durable Temporal Workflow: TrailSafetyWorkflow.

Orchestrates multi-hour outdoor sessions with persistent dead-man's switch timers,
asynchronous signals, non-blocking queries, and TabPFN Bayesian risk assessment activities.
"""

from datetime import timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.temporal.activities import (
        evaluate_tabpfn_risk_activity,
        dispatch_emergency_alert_activity,
        log_trail_telemetry_activity,
    )


class TrailSessionParams(BaseModel):
    """Parameters for launching a TrailSafetyWorkflow session."""

    hiker_id: str
    trail_id: str
    trail_name: str
    checkpoints: List[Dict[str, Any]]
    checkpoint_timeout_seconds: int = 45 * 60
    grace_period_seconds: int = 10 * 60
    initial_telemetry: Optional[Dict[str, Any]] = None


@workflow.defn(sandboxed=False)
class TrailSafetyWorkflow:
    """Durable state machine managing outdoor dead-man switch and risk inference."""

    def __init__(self) -> None:
        self.params: Optional[TrailSessionParams] = None
        self.status: str = "INITIALIZED"
        self.current_checkpoint_idx: int = 0
        self.total_checkpoints: int = 0
        self.last_check_in_time: str = ""
        self.latest_telemetry: Dict[str, Any] = {}
        self.latest_risk: Dict[str, Any] = {}
        self.audit_events: List[Dict[str, Any]] = []

        # Internal signal triggers
        self._signal_received: bool = False
        self._sos_triggered: bool = False
        self._sos_reason: str = ""
        self._extended_seconds: int = 0
        self._hike_completed: bool = False
        self._hike_cancelled: bool = False

    @workflow.signal
    def check_in(self, payload: Dict[str, Any]) -> None:
        """Signal received when hiker checks in at a waypoint via NFC, QR, or app tap."""
        self._signal_received = True
        self.latest_telemetry = payload.get("telemetry", {})
        self.current_checkpoint_idx = min(self.current_checkpoint_idx + 1, self.total_checkpoints)
        checkpoint_id = payload.get("checkpoint_id", f"cp-{self.current_checkpoint_idx}")
        now_iso = workflow.now().isoformat()
        self.last_check_in_time = now_iso
        self.audit_events.append({
            "event": "check_in_signal_received",
            "checkpoint_id": checkpoint_id,
            "timestamp": now_iso,
            "telemetry": self.latest_telemetry,
        })

    @workflow.signal
    def extend_window(self, minutes: int) -> None:
        """Signal received when hiker requests rest or photo time extension."""
        self._extended_seconds += max(1, minutes) * 60
        self.audit_events.append({
            "event": "window_extended",
            "additional_minutes": minutes,
            "timestamp": workflow.now().isoformat(),
        })

    @workflow.signal
    def emergency_sos(self, reason: str) -> None:
        """Signal received when hiker or device triggers immediate panic SOS."""
        self._sos_triggered = True
        self._sos_reason = reason or "Manual emergency SOS panic button pressed"
        self.audit_events.append({
            "event": "manual_sos_triggered",
            "reason": self._sos_reason,
            "timestamp": workflow.now().isoformat(),
        })

    @workflow.signal
    def complete_hike(self) -> None:
        """Signal received when hiker safely finishes trail."""
        self._hike_completed = True
        self.audit_events.append({
            "event": "hike_completed_signal",
            "timestamp": workflow.now().isoformat(),
        })

    @workflow.signal
    def cancel_hike(self, reason: str) -> None:
        """Signal received when hiker cancels trip before trailhead or early abort."""
        self._hike_cancelled = True
        self.audit_events.append({
            "event": "hike_cancelled_signal",
            "reason": reason,
            "timestamp": workflow.now().isoformat(),
        })

    @workflow.query
    def get_hiker_status(self) -> Dict[str, Any]:
        """Non-blocking query returning current state machine snapshot."""
        return {
            "status": self.status,
            "hiker_id": self.params.hiker_id if self.params else "unknown",
            "trail_name": self.params.trail_name if self.params else "unknown",
            "current_checkpoint_idx": self.current_checkpoint_idx,
            "total_checkpoints": self.total_checkpoints,
            "current_checkpoint": (
                self.params.checkpoints[self.current_checkpoint_idx]
                if self.params and self.current_checkpoint_idx < len(self.params.checkpoints)
                else None
            ),
            "last_check_in_time": self.last_check_in_time,
            "latest_telemetry": self.latest_telemetry,
            "latest_risk": self.latest_risk,
            "extended_seconds": self._extended_seconds,
            "sos_triggered": self._sos_triggered,
        }

    @workflow.query
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Non-blocking query returning chronological audit log."""
        return self.audit_events

    @workflow.run
    async def run(self, params_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Workflow execution managing dead-man switch intervals and risk analysis."""
        self.params = TrailSessionParams(**params_dict)
        self.total_checkpoints = len(self.params.checkpoints)
        self.status = "ACTIVE"
        now_iso = workflow.now().isoformat()
        self.last_check_in_time = now_iso

        self.audit_events.append({
            "event": "session_started",
            "hiker_id": self.params.hiker_id,
            "trail_name": self.params.trail_name,
            "timestamp": now_iso,
        })

        # Evaluate initial baseline telemetry if provided
        if self.params.initial_telemetry:
            self.latest_telemetry = self.params.initial_telemetry
            risk = await workflow.execute_activity(
                evaluate_tabpfn_risk_activity,
                self.latest_telemetry,
                start_to_close_timeout=timedelta(seconds=90),
            )
            self.latest_risk = risk

        # Main Checkpoint Traversal Loop
        while self.current_checkpoint_idx < self.total_checkpoints:
            target_cp = self.params.checkpoints[self.current_checkpoint_idx]
            self.audit_events.append({
                "event": "leg_started",
                "checkpoint_index": self.current_checkpoint_idx,
                "target_checkpoint": target_cp.get("name", f"CP-{self.current_checkpoint_idx + 1}"),
                "timestamp": workflow.now().isoformat(),
            })

            # Calculate leg window duration
            leg_window_secs = self.params.checkpoint_timeout_seconds + self._extended_seconds
            self._extended_seconds = 0
            self._signal_received = False

            # 1. Wait condition for check-in during normal window
            try:
                await workflow.wait_condition(
                    lambda: (
                        self._signal_received
                        or self._sos_triggered
                        or self._hike_completed
                        or self._hike_cancelled
                    ),
                    timeout=timedelta(seconds=leg_window_secs),
                )
            except TimeoutError:
                # Normal window expired without signal
                pass

            # Check manual SOS
            if self._sos_triggered:
                return await self._escalate_emergency(f"Emergency SOS triggered: {self._sos_reason}")

            # Check voluntary completion/cancellation
            if self._hike_completed:
                self.status = "COMPLETED"
                return self._build_summary("Hike completed by user.")
            if self._hike_cancelled:
                self.status = "CANCELLED"
                return self._build_summary("Hike cancelled.")

            # If signal was received during normal window
            if self._signal_received:
                await self._process_successful_signal()
                continue

            # 2. Transition to GRACE PERIOD
            self.status = "GRACE_PERIOD"
            self.audit_events.append({
                "event": "grace_period_entered",
                "checkpoint_index": self.current_checkpoint_idx,
                "timestamp": workflow.now().isoformat(),
            })

            try:
                await workflow.wait_condition(
                    lambda: (
                        self._signal_received
                        or self._sos_triggered
                        or self._hike_completed
                        or self._hike_cancelled
                    ),
                    timeout=timedelta(seconds=self.params.grace_period_seconds),
                )
            except TimeoutError:
                # Grace period expired without signal -> DEAD-MAN SWITCH TRIGGERED!
                pass

            # Check manual SOS
            if self._sos_triggered:
                return await self._escalate_emergency(f"Emergency SOS triggered: {self._sos_reason}")

            # Check completion/cancellation during grace period
            if self._hike_completed:
                self.status = "COMPLETED"
                return self._build_summary("Hike completed during grace period.")
            if self._hike_cancelled:
                self.status = "CANCELLED"
                return self._build_summary("Hike cancelled during grace period.")

            # If check-in arrived during grace period
            if self._signal_received:
                await self._process_successful_signal()
                self.status = "ACTIVE"
                continue

            # 3. Escalation: DEAD-MAN SWITCH EXPIRED
            return await self._escalate_emergency(
                f"Missed checkpoint '{target_cp.get('name')}' beyond timeout and grace period."
            )

        self.status = "COMPLETED"
        return self._build_summary("Hike successfully completed all checkpoints.")

    async def _process_successful_signal(self) -> None:
        """Processes successful check-in signal and evaluates TabPFN risk."""
        if self.latest_telemetry:
            risk = await workflow.execute_activity(
                evaluate_tabpfn_risk_activity,
                self.latest_telemetry,
                start_to_close_timeout=timedelta(seconds=90),
            )
            self.latest_risk = risk

            await workflow.execute_activity(
                log_trail_telemetry_activity,
                {
                    "hiker_id": self.params.hiker_id,
                    "trail_id": self.params.trail_id,
                    "checkpoint_idx": self.current_checkpoint_idx,
                    "telemetry": self.latest_telemetry,
                    "risk": risk,
                },
                start_to_close_timeout=timedelta(seconds=15),
            )

    async def _escalate_emergency(self, reason: str) -> Dict[str, Any]:
        """Dispatches emergency alerts and halts workflow."""
        self.status = "EMERGENCY_DISPATCHED"
        last_cp = (
            self.params.checkpoints[self.current_checkpoint_idx]
            if self.params and self.current_checkpoint_idx < len(self.params.checkpoints)
            else {"name": "Trailhead", "id": "cp-0", "latitude": 15.0, "longitude": 74.0}
        )

        alert_payload = {
            "hiker_id": self.params.hiker_id if self.params else "Unknown Hiker",
            "trail_name": self.params.trail_name if self.params else "Unknown Trail",
            "last_checkpoint_id": last_cp.get("id", "cp-unknown"),
            "last_checkpoint_name": last_cp.get("name", "Unknown Waypoint"),
            "latitude": float(last_cp.get("latitude", 15.0)),
            "longitude": float(last_cp.get("longitude", 74.0)),
            "hours_elapsed": float(self.latest_telemetry.get("hours_elapsed", 0.0)),
            "reason": reason,
            "hazard_probability": float(self.latest_risk.get("hazard_probability", 0.95)),
            "water_remaining_ml": float(self.latest_telemetry.get("water_remaining_ml", 0.0)),
        }

        dispatch_result = await workflow.execute_activity(
            dispatch_emergency_alert_activity,
            alert_payload,
            start_to_close_timeout=timedelta(seconds=30),
        )

        self.audit_events.append({
            "event": "emergency_dispatched",
            "alert": alert_payload,
            "dispatch_result": dispatch_result,
            "timestamp": workflow.now().isoformat(),
        })

        return {
            "status": "EMERGENCY_DISPATCHED",
            "reason": reason,
            "dispatch_result": dispatch_result,
            "audit_trail": self.audit_events,
        }

    def _build_summary(self, message: str) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message": message,
            "hiker_id": self.params.hiker_id if self.params else "",
            "trail_name": self.params.trail_name if self.params else "",
            "checkpoints_completed": self.current_checkpoint_idx,
            "total_checkpoints": self.total_checkpoints,
            "latest_risk": self.latest_risk,
            "audit_trail": self.audit_events,
        }
