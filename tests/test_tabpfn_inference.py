"""Unit tests verifying authentic Prior Labs TabPFN in-context Bayesian inference."""

import pytest
from src.ml.tabpfn_engine import HikerTelemetry, RiskAssessmentResult, TabPFNRiskEngine


def test_hiker_telemetry_validation():
    """Verifies that 7D telemetry vector validates constraints."""
    telem = HikerTelemetry(
        elevation_delta_m=150.0,
        pace_min_per_km=12.5,
        hours_elapsed=2.0,
        ambient_temp_c=27.0,
        water_remaining_ml=1500.0,
        cadence_spm=110.0,
        terrain_roughness_idx=1.8,
    )
    arr = telem.to_array()
    assert arr.shape == (1, 7)
    assert arr[0, 0] == 150.0


def test_tabpfn_nominal_hike_evaluation():
    """Verifies TabPFN Bayesian prediction for fresh, well-hydrated hiker."""
    engine = TabPFNRiskEngine.get_instance()
    nominal_telem = HikerTelemetry(
        elevation_delta_m=40.0,
        pace_min_per_km=10.5,
        hours_elapsed=0.5,
        ambient_temp_c=22.0,
        water_remaining_ml=2000.0,
        cadence_spm=122.0,
        terrain_roughness_idx=1.0,
    )
    res: RiskAssessmentResult = engine.evaluate(nominal_telem)

    assert isinstance(res, RiskAssessmentResult)
    assert 0.0 <= res.hazard_probability <= 1.0
    # Fresh hiker should have low hazard probability
    assert res.hazard_probability < 0.35
    assert res.is_hazard is False
    assert res.projected_water_deficit_ml < 200.0
    assert "Prior Labs TabPFN" in res.model_mode


def test_tabpfn_exhaustion_distress_evaluation():
    """Verifies TabPFN Bayesian escalation for severely fatigued, dehydrated hiker."""
    engine = TabPFNRiskEngine.get_instance()
    distress_telem = HikerTelemetry(
        elevation_delta_m=480.0,
        pace_min_per_km=27.0,
        hours_elapsed=7.5,
        ambient_temp_c=35.5,
        water_remaining_ml=0.0,
        cadence_spm=52.0,
        terrain_roughness_idx=3.8,
    )
    res: RiskAssessmentResult = engine.evaluate(distress_telem)

    assert isinstance(res, RiskAssessmentResult)
    # Severe distress should trigger elevated hazard probability and water deficit
    assert res.hazard_probability >= 0.70
    assert res.is_hazard is True
    assert res.hazard_label == 1
    assert res.projected_water_deficit_ml > 500.0
    assert "hazard" in res.recommendation.lower() or "fatigue" in res.recommendation.lower() or "halt" in res.recommendation.lower()


def test_tabpfn_singleton_and_model_metadata():
    """Verifies engine singleton reuse and metadata integrity."""
    engine1 = TabPFNRiskEngine.get_instance()
    engine2 = TabPFNRiskEngine.get_instance()
    assert engine1 is engine2
    assert engine1.is_fitted is True


def test_tabpfn_caution_boundary_behavior():
    """Verifies model confidence and actionable recommendation across caution margins."""
    engine = TabPFNRiskEngine.get_instance()
    moderate_telem = HikerTelemetry(
        elevation_delta_m=200.0,
        pace_min_per_km=14.0,
        hours_elapsed=3.0,
        ambient_temp_c=29.0,
        water_remaining_ml=1100.0,
        cadence_spm=105.0,
        terrain_roughness_idx=2.0,
    )
    res = engine.evaluate(moderate_telem)
    assert 0.0 <= res.confidence <= 1.0
    assert len(res.recommendation) > 10

