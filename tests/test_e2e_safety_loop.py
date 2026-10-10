"""End-to-End Safety Loop and API Integration Test Suite.

Verifies the full lifecycle: session launch, phone telemetry ingestion,
Prior Labs TabPFN Bayesian hazard evaluation, checkpoint signals,
window extension, and emergency dispatch.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from src.server.app import app


@pytest.mark.asyncio
async def test_e2e_full_hike_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. System status check
        status_res = await client.get("/api/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["status"] == "operational"
        assert status_data["tabpfn_ready"] is True
        assert status_data["trails_loaded"] >= 2

        # 2. Trails query
        trails_res = await client.get("/api/trails")
        assert trails_res.status_code == 200
        trails = trails_res.json()
        assert len(trails) >= 2
        trail = trails[0]

        # 3. Direct TabPFN risk evaluation
        telem_payload = {
            "elevation_delta_m": 80.0,
            "pace_min_per_km": 11.2,
            "hours_elapsed": 1.2,
            "ambient_temp_c": 25.0,
            "water_remaining_ml": 1800.0,
            "cadence_spm": 116.0,
            "terrain_roughness_idx": 1.3,
        }
        eval_res = await client.post("/api/risk/evaluate", json=telem_payload)
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert "hazard_probability" in eval_data
        assert "projected_water_deficit_ml" in eval_data
        assert eval_data["is_hazard"] is False

        # 4. Initiate hike session
        start_payload = {
            "hiker_id": "Test Hiker",
            "trail_id": trail["trail_id"],
            "timeout_minutes": 45,
            "emergency_contact": "+919999999999",
            "initial_telemetry": telem_payload,
        }
        start_res = await client.post("/api/hikes/start", json=start_payload)
        assert start_res.status_code == 200
        session = start_res.json()
        session_id = session["session_id"]
        assert session["status"] == "ACTIVE"
        assert session["current_checkpoint_idx"] == 0

        # 5. Transmit checkpoint check-in
        check_in_payload = {
            "checkpoint_id": trail["checkpoints"][0]["id"],
            "telemetry": {
                "elevation_delta_m": 120.0,
                "pace_min_per_km": 12.0,
                "hours_elapsed": 1.8,
                "ambient_temp_c": 26.5,
                "water_remaining_ml": 1500.0,
                "cadence_spm": 112.0,
                "terrain_roughness_idx": 1.8,
            },
        }
        ci_res = await client.post(f"/api/hikes/{session_id}/check-in", json=check_in_payload)
        assert ci_res.status_code == 200
        updated_session = ci_res.json()
        assert updated_session["current_checkpoint_idx"] == 1
        assert "hazard_probability" in updated_session["latest_risk"]

        # 6. Extend safety window
        ext_res = await client.post(f"/api/hikes/{session_id}/extend", json={"minutes": 15})
        assert ext_res.status_code == 200
        assert ext_res.json()["status"] == "extended"

        # 7. Query live session status
        q_res = await client.get(f"/api/hikes/{session_id}/status")
        assert q_res.status_code == 200
        q_data = q_res.json()
        assert q_data["session_id"] == session_id
        assert q_data["remaining_seconds"] > 0

        # 8. Trigger emergency SOS panic button
        sos_payload = {
            "reason": "Sudden heat exhaustion and disoriented",
            "latitude": 15.0892,
            "longitude": 74.2154,
        }
        sos_res = await client.post(f"/api/hikes/{session_id}/sos", json=sos_payload)
        assert sos_res.status_code == 200
        sos_data = sos_res.json()
        assert sos_data["status"] == "EMERGENCY_DISPATCHED"
        assert "audit" in sos_data

        # 9. Verify legal pages and static web app
        privacy_res = await client.get("/privacy")
        assert privacy_res.status_code == 200
        assert "Privacy Policy" in privacy_res.text

        terms_res = await client.get("/terms")
        assert terms_res.status_code == 200
        assert "Terms and Conditions" in terms_res.text

        index_res = await client.get("/")
        assert index_res.status_code == 200
        assert "TrailSafe" in index_res.text
