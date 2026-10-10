"""Temporal Activities for TrailSafe: TabPFN inference, emergency dispatch, and ledger logging."""

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Any
from temporalio import activity

from src.config import settings
from src.ml.tabpfn_engine import HikerTelemetry, TabPFNRiskEngine
from src.dispatch.notifier import EmergencyDispatchMessage, EmergencyDispatcher


@activity.defn
async def evaluate_tabpfn_risk_activity(telemetry_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Activity executing Prior Labs TabPFN Bayesian in-context tabular inference."""
    activity.logger.info(f"Evaluating TabPFN risk for telemetry: {telemetry_dict}")
    telemetry = HikerTelemetry(**telemetry_dict)
    engine = TabPFNRiskEngine.get_instance()
    result = await asyncio.to_thread(engine.evaluate, telemetry)
    return result.model_dump()


@activity.defn
async def dispatch_emergency_alert_activity(alert_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Activity dispatching emergency alerts across Telegram and SMS channels."""
    activity.logger.warning(f"Executing emergency alert dispatch: {alert_payload}")
    msg = EmergencyDispatchMessage(**alert_payload)
    dispatcher = EmergencyDispatcher()
    audit_record = await asyncio.to_thread(dispatcher.dispatch, msg)
    return audit_record


@activity.defn
async def log_trail_telemetry_activity(log_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Activity appending validated trail observation to immutable append-only ledger."""
    ledger_path = settings.DATA_DIR / "trail_ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": log_payload,
    }

    def _write_ledger():
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    await asyncio.to_thread(_write_ledger)
    return {"status": "persisted", "timestamp": entry["timestamp"]}

