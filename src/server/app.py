"""FastAPI Server exposing TrailSafe REST API and Mobile Phone Web Application.

Bridges mobile phone sensors, Temporal durable workflows, and Prior Labs TabPFN
Bayesian tabular inference.
"""

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.config import settings
from src.ml.tabpfn_engine import HikerTelemetry, RiskAssessmentResult, TabPFNRiskEngine
from src.ml.benchmark_eval import run_benchmark
from src.dispatch.notifier import EmergencyDispatchMessage, EmergencyDispatcher
from src.temporal.worker import create_temporal_client
from src.temporal.workflows import TrailSafetyWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trailsafe.server")

app = FastAPI(
    title="TrailSafe API & Field Application",
    description="Offline Solo Hiker Dead-Man's Switch & In-Context Tabular Risk Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = settings.BASE_DIR / "src" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def startup_warmup():
    logger.info("Pre-warming Prior Labs TabPFN Bayesian Foundation Model in RAM...")
    try:
        engine = TabPFNRiskEngine.get_instance()
        dummy = HikerTelemetry(
            elevation_delta_m=0.0,
            pace_min_per_km=11.0,
            hours_elapsed=0.1,
            ambient_temp_c=25.0,
            water_remaining_ml=2000.0,
            cadence_spm=120.0,
            terrain_roughness_idx=1.1,
        )
        engine.evaluate(dummy)
        logger.info("Prior Labs TabPFN is hot in RAM and ready for instantaneous inference.")
    except Exception as e:
        logger.warning(f"TabPFN startup notice: {e}")


# In-memory session registry for mobile state synchronization
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}


class StartHikeRequest(BaseModel):
    hiker_id: str = Field(default="Solo Explorer")
    trail_id: str = Field(default="netravali-ridge")
    timeout_minutes: int = Field(default=45, ge=1, le=240)
    emergency_contact: Optional[str] = None
    initial_telemetry: Optional[Dict[str, Any]] = None


class CheckInRequest(BaseModel):
    checkpoint_id: str
    telemetry: Dict[str, Any]


class ExtendRequest(BaseModel):
    minutes: int = Field(default=15, ge=1, le=120)


class SosRequest(BaseModel):
    reason: str = Field(default="Manual SOS triggered by solo hiker")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


def load_all_trails() -> List[Dict[str, Any]]:
    """Loads configured trails from JSON fixtures."""
    fp = settings.DATA_DIR / "test_checkpoints.json"
    if not fp.exists():
        return []
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/", response_class=FileResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>TrailSafe Mobile App loading...</h1>")
    return FileResponse(index_file)


@app.get("/privacy", response_class=FileResponse)
async def serve_privacy():
    privacy_file = STATIC_DIR / "privacy.html"
    return FileResponse(privacy_file)


@app.get("/terms", response_class=FileResponse)
async def serve_terms():
    terms_file = STATIC_DIR / "terms.html"
    return FileResponse(terms_file)


@app.get("/api/status")
async def get_system_status():
    """Checks cluster connection, TabPFN readiness, and trails data."""
    temporal_connected = False
    try:
        client = await create_temporal_client()
        temporal_connected = True
    except Exception:
        temporal_connected = False

    tabpfn_ready = False
    try:
        TabPFNRiskEngine.get_instance()
        tabpfn_ready = True
    except Exception as e:
        logger.warning(f"TabPFN init status: {e}")

    trails = load_all_trails()

    return {
        "status": "operational",
        "temporal_connected": temporal_connected,
        "temporal_host": settings.TEMPORAL_TARGET_HOST,
        "tabpfn_ready": tabpfn_ready,
        "tabpfn_mode": settings.TABPFN_MODE,
        "trails_loaded": len(trails),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/trails")
async def list_trails():
    """Returns available trails and waypoint coordinates."""
    return load_all_trails()


@app.post("/api/risk/evaluate")
async def evaluate_risk(telemetry_data: HikerTelemetry) -> Dict[str, Any]:
    """Evaluates 7D biometric and environmental telemetry with Prior Labs TabPFN."""
    engine = TabPFNRiskEngine.get_instance()
    result = engine.evaluate(telemetry_data)
    return result.model_dump()


@app.get("/api/benchmark/run")
async def run_benchmark_endpoint(recalculate: bool = False):
    """Runs empirical Leave-One-Out CV benchmark of TabPFN vs scikit-learn baselines."""
    return run_benchmark(force_recompute=recalculate)


@app.post("/api/hikes/start")
async def start_hike(req: StartHikeRequest):
    """Initiates outdoor dead-man switch session."""
    trails = load_all_trails()
    matched_trail = next((t for t in trails if t["trail_id"] == req.trail_id), None)
    if not matched_trail:
        if trails:
            matched_trail = trails[0]
        else:
            raise HTTPException(status_code=404, detail="No trails loaded")

    checkpoints = matched_trail["checkpoints"]
    session_id = f"trailsafe-{matched_trail['trail_id']}-{int(time.time())}"

    # Default initial telemetry
    first_cp = checkpoints[0]
    initial_telem = req.initial_telemetry or {
        "elevation_delta_m": 0.0,
        "pace_min_per_km": float(first_cp.get("expected_pace_min_per_km", 11.0)),
        "hours_elapsed": 0.1,
        "ambient_temp_c": 25.0,
        "water_remaining_ml": 2000.0,
        "cadence_spm": 120.0,
        "terrain_roughness_idx": float(first_cp.get("terrain_roughness_idx", 1.1)),
    }

    # In-context evaluation with Prior Labs TabPFN
    t_tabpfn = time.time()
    risk_engine = TabPFNRiskEngine.get_instance()
    initial_risk = await asyncio.to_thread(
        lambda: risk_engine.evaluate(HikerTelemetry(**initial_telem)).model_dump()
    )
    logger.info(f"TabPFN initial evaluation completed in {time.time() - t_tabpfn:.2f}s")

    # Attempt to start Temporal durable workflow
    t_temporal = time.time()
    temporal_workflow_id = None
    try:
        client = await create_temporal_client(timeout_seconds=1.0)
        logger.info(f"Temporal client connected in {time.time() - t_temporal:.2f}s")
        params = {
            "hiker_id": req.hiker_id,
            "trail_id": matched_trail["trail_id"],
            "trail_name": matched_trail["trail_name"],
            "checkpoints": checkpoints,
            "checkpoint_timeout_seconds": req.timeout_minutes * 60,
            "grace_period_seconds": settings.SAFETY_GRACE_PERIOD_MINUTES * 60,
            "initial_telemetry": initial_telem,
        }
        await client.start_workflow(
            TrailSafetyWorkflow.run,
            params,
            id=session_id,
            task_queue=settings.TEMPORAL_TASK_QUEUE,
        )
        temporal_workflow_id = session_id
        logger.info(f"Started Temporal workflow: {session_id}")
    except Exception as e:
        logger.warning(f"Temporal cluster start skipped or offline ({e}). Running server state machine.")

    timeout_seconds = req.timeout_minutes * 60
    session_data = {
        "session_id": session_id,
        "temporal_workflow_id": temporal_workflow_id,
        "hiker_id": req.hiker_id,
        "trail": matched_trail,
        "status": "ACTIVE",
        "current_checkpoint_idx": 0,
        "total_checkpoints": len(checkpoints),
        "timeout_seconds": timeout_seconds,
        "deadline_timestamp": time.time() + timeout_seconds,
        "last_check_in_time": datetime.now(timezone.utc).isoformat(),
        "latest_telemetry": initial_telem,
        "latest_risk": initial_risk,
        "audit_trail": [
            {
                "event": "session_started",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checkpoint": first_cp["name"],
            }
        ],
    }
    ACTIVE_SESSIONS[session_id] = session_data
    return session_data


def get_or_reconstruct_session(session_id: str, fallback_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    session = ACTIVE_SESSIONS.get(session_id)
    if session:
        return session

    trails = load_all_trails()
    matched_trail = None
    for t in trails:
        if t["trail_id"] in session_id:
            matched_trail = t
            break
    if not matched_trail and trails:
        matched_trail = trails[0]

    if not matched_trail:
        raise HTTPException(status_code=404, detail="Hike session not found")

    telem = fallback_telemetry or {
        "elevation_delta_m": 0.0,
        "pace_min_per_km": 11.0,
        "hours_elapsed": 0.5,
        "ambient_temp_c": 25.0,
        "water_remaining_ml": 1800.0,
        "cadence_spm": 120.0,
        "terrain_roughness_idx": 1.1,
    }

    session = {
        "session_id": session_id,
        "temporal_workflow_id": None,
        "hiker_id": "Kanak Waradkar",
        "trail": matched_trail,
        "status": "ACTIVE",
        "current_checkpoint_idx": 0,
        "total_checkpoints": len(matched_trail["checkpoints"]),
        "timeout_seconds": 2700,
        "deadline_timestamp": time.time() + 2700,
        "last_check_in_time": datetime.now(timezone.utc).isoformat(),
        "latest_telemetry": telem,
        "latest_risk": {},
        "audit_trail": [{"event": "session_reconnected", "timestamp": datetime.now(timezone.utc).isoformat()}],
    }
    ACTIVE_SESSIONS[session_id] = session
    logger.info(f"Reconstructed active session {session_id} for trail {matched_trail['trail_name']}")
    return session


@app.post("/api/reset")
@app.get("/api/reset")
async def reset_all_sessions():
    """Resets in-memory sessions."""
    ACTIVE_SESSIONS.clear()
    return {"status": "cleared", "message": "All sessions reset."}


@app.post("/api/hikes/{session_id}/check-in")
async def record_check_in(session_id: str, req: CheckInRequest):
    """Processes waypoint signal and evaluates telemetry."""
    session = get_or_reconstruct_session(session_id, req.telemetry)

    telemetry_obj = HikerTelemetry(**req.telemetry)
    risk_result = await asyncio.to_thread(
        lambda: TabPFNRiskEngine.get_instance().evaluate(telemetry_obj).model_dump()
    )

    # Forward signal to Temporal if connected
    if session.get("temporal_workflow_id"):
        try:
            client = await create_temporal_client(timeout_seconds=1.0)
            handle = client.get_workflow_handle(session["temporal_workflow_id"])
            await handle.signal(
                TrailSafetyWorkflow.check_in,
                {"checkpoint_id": req.checkpoint_id, "telemetry": req.telemetry},
            )
        except Exception as e:
            logger.warning(f"Failed to signal Temporal workflow: {e}")

    session["current_checkpoint_idx"] = min(
        session["current_checkpoint_idx"] + 1, session["total_checkpoints"]
    )
    session["latest_telemetry"] = req.telemetry
    session["latest_risk"] = risk_result
    session["last_check_in_time"] = datetime.now(timezone.utc).isoformat()
    session["deadline_timestamp"] = time.time() + session["timeout_seconds"]

    if session["current_checkpoint_idx"] >= session["total_checkpoints"]:
        session["status"] = "COMPLETED"

    session["audit_trail"].append({
        "event": "check_in_verified",
        "checkpoint_id": req.checkpoint_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hazard_probability": risk_result["hazard_probability"],
    })

    return session


@app.post("/api/hikes/{session_id}/extend")
async def extend_session_window(session_id: str, req: ExtendRequest):
    """Extends dead-man timer for rest or photo break."""
    session = get_or_reconstruct_session(session_id)

    additional_seconds = req.minutes * 60
    session["deadline_timestamp"] += additional_seconds

    if session.get("temporal_workflow_id"):
        try:
            client = await create_temporal_client(timeout_seconds=1.0)
            handle = client.get_workflow_handle(session["temporal_workflow_id"])
            await handle.signal(TrailSafetyWorkflow.extend_window, req.minutes)
        except Exception as e:
            logger.warning(f"Failed to signal Temporal window extension: {e}")

    session["audit_trail"].append({
        "event": "window_extended",
        "additional_minutes": req.minutes,
        "new_deadline": session["deadline_timestamp"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "extended", "deadline_timestamp": session["deadline_timestamp"]}


@app.post("/api/hikes/{session_id}/sos")
async def trigger_emergency_sos(session_id: str, req: SosRequest):
    """Triggers immediate emergency SOS rescue beacon."""
    session = get_or_reconstruct_session(session_id)

    session["status"] = "EMERGENCY_DISPATCHED"

    # Forward signal to Temporal workflow
    if session.get("temporal_workflow_id"):
        try:
            client = await create_temporal_client(timeout_seconds=1.0)
            handle = client.get_workflow_handle(session["temporal_workflow_id"])
            await handle.signal(TrailSafetyWorkflow.emergency_sos, req.reason)
        except Exception as e:
            logger.warning(f"Failed to signal Temporal SOS: {e}")

    # Immediate dispatch
    current_idx = min(session["current_checkpoint_idx"], len(session["trail"]["checkpoints"]) - 1)
    cp = session["trail"]["checkpoints"][current_idx]
    lat = req.latitude or cp.get("latitude", 15.0892)
    lon = req.longitude or cp.get("longitude", 74.2154)

    msg = EmergencyDispatchMessage(
        hiker_id=session["hiker_id"],
        trail_name=session["trail"]["trail_name"],
        last_checkpoint_id=cp["id"],
        last_checkpoint_name=cp["name"],
        latitude=lat,
        longitude=lon,
        hours_elapsed=float(session["latest_telemetry"].get("hours_elapsed", 1.0)),
        reason=req.reason,
        hazard_probability=float(session["latest_risk"].get("hazard_probability", 0.95)),
        water_remaining_ml=float(session["latest_telemetry"].get("water_remaining_ml", 0.0)),
    )
    dispatcher = EmergencyDispatcher()
    audit_rec = dispatcher.dispatch(msg)

    session["audit_trail"].append({
        "event": "emergency_sos_dispatched",
        "reason": req.reason,
        "dispatch_record": audit_rec,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {"status": "EMERGENCY_DISPATCHED", "audit": audit_rec}


@app.get("/api/hikes/{session_id}/status")
async def get_session_status(session_id: str):
    """Retrieves live state machine snapshot and countdown seconds."""
    session = get_or_reconstruct_session(session_id)

    now = time.time()
    remaining_seconds = max(0, int(session["deadline_timestamp"] - now))

    # Auto dead-man expiration check if running locally
    if remaining_seconds == 0 and session["status"] == "ACTIVE":
        session["status"] = "GRACE_PERIOD"

    # Query Temporal if workflow exists
    if session.get("temporal_workflow_id"):
        try:
            client = await create_temporal_client(timeout_seconds=1.0)
            handle = client.get_workflow_handle(session["temporal_workflow_id"])
            temporal_status = await handle.query(TrailSafetyWorkflow.get_hiker_status)
            session["status"] = temporal_status.get("status", session["status"])
            session["latest_risk"] = temporal_status.get("latest_risk", session["latest_risk"])
        except Exception:
            pass

    return {
        **session,
        "remaining_seconds": remaining_seconds,
        "current_time": now,
    }


@app.post("/api/hikes/{session_id}/finish")
async def finish_hike(session_id: str):
    """Safely terminates active hike session."""
    session = get_or_reconstruct_session(session_id)

    session["status"] = "COMPLETED"
    if session.get("temporal_workflow_id"):
        try:
            client = await create_temporal_client(timeout_seconds=1.0)
            handle = client.get_workflow_handle(session["temporal_workflow_id"])
            await handle.signal(TrailSafetyWorkflow.complete_hike)
        except Exception:
            pass

    return {"status": "COMPLETED", "message": "Hike finished safely."}
