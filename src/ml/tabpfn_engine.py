"""Prior Labs TabPFN In-Context Bayesian Risk Engine for Solo Hiker Safety.

Performs zero-hyperparameter, single-forward-pass Bayesian tabular inference
over physical biometrics and environmental telemetry without gradient descent.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from tabpfn import TabPFNClassifier, TabPFNRegressor

from src.config import settings

FEATURE_COLUMNS = [
    "elevation_delta_m",
    "pace_min_per_km",
    "hours_elapsed",
    "ambient_temp_c",
    "water_remaining_ml",
    "cadence_spm",
    "terrain_roughness_idx",
]


class HikerTelemetry(BaseModel):
    """Calibrated 7D telemetry vector collected at trail checkpoints."""

    elevation_delta_m: float = Field(
        ..., description="Net vertical elevation gained or lost over the leg (meters)"
    )
    pace_min_per_km: float = Field(
        ..., ge=1.0, le=90.0, description="Moving pace (min/km)"
    )
    hours_elapsed: float = Field(
        ..., ge=0.0, le=48.0, description="Total active hours on the trail"
    )
    ambient_temp_c: float = Field(
        ..., ge=-20.0, le=55.0, description="Environmental ambient temperature (°C)"
    )
    water_remaining_ml: float = Field(
        ..., ge=0.0, le=10000.0, description="Remaining fluid volume in pack (mL)"
    )
    cadence_spm: float = Field(
        ..., ge=0.0, le=240.0, description="Cadence in steps per minute"
    )
    terrain_roughness_idx: float = Field(
        ..., ge=1.0, le=5.0, description="Trail difficulty roughness rating (1.0 to 5.0)"
    )

    def to_array(self) -> np.ndarray:
        return np.array(
            [
                [
                    self.elevation_delta_m,
                    self.pace_min_per_km,
                    self.hours_elapsed,
                    self.ambient_temp_c,
                    self.water_remaining_ml,
                    self.cadence_spm,
                    self.terrain_roughness_idx,
                ]
            ],
            dtype=np.float32,
        )

    def to_dict(self) -> Dict[str, float]:
        return {col: getattr(self, col) for col in FEATURE_COLUMNS}


class RiskAssessmentResult(BaseModel):
    """In-context Bayesian risk evaluation result."""

    hazard_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Bayesian posterior P(hazard)"
    )
    hazard_label: int = Field(
        ..., description="Binary classification (0=nominal, 1=distress)"
    )
    projected_water_deficit_ml: float = Field(
        ..., ge=0.0, description="Expected fluid shortfall (mL)"
    )
    is_hazard: bool = Field(
        ..., description="True if hazard_probability >= threshold"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model certainty metric"
    )
    model_mode: str = Field(
        default="Prior Labs TabPFN Bayesian Foundation Model",
        description="Inference provider signature",
    )
    recommendation: str = Field(
        ..., description="Actionable field guidance"
    )


class TabPFNRiskEngine:
    """Manages TabPFNClassifier and TabPFNRegressor with historical trail priors."""

    _instance: Optional["TabPFNRiskEngine"] = None

    def __init__(self, data_path: Optional[Union[str, Path]] = None) -> None:
        self.data_path = Path(data_path) if data_path else settings.DATA_DIR / "sample_trail_history.csv"
        self.classifier = TabPFNClassifier(
            n_estimators=settings.TABPFN_N_ESTIMATORS,
            device=settings.TABPFN_DEVICE,
        )
        self.regressor = TabPFNRegressor(
            n_estimators=settings.TABPFN_N_ESTIMATORS,
            device=settings.TABPFN_DEVICE,
        )
        self.is_fitted = False
        self._fit_context()

    @classmethod
    def get_instance(cls, data_path: Optional[Union[str, Path]] = None) -> "TabPFNRiskEngine":
        if cls._instance is None:
            cls._instance = cls(data_path=data_path)
        return cls._instance

    def _fit_context(self) -> None:
        """Loads historical trail observations into the TabPFN in-context buffer."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Historical telemetry CSV not found at {self.data_path}")

        df = pd.read_csv(self.data_path)
        X = df[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
        y_cls = df["hazard_label"].to_numpy(dtype=np.int64)
        y_reg = df["water_deficit_ml"].to_numpy(dtype=np.float32)

        # TabPFN fits instantly via in-context memory
        self.classifier.fit(X, y_cls)
        self.regressor.fit(X, y_reg)
        self.is_fitted = True

    def evaluate(self, telemetry: HikerTelemetry) -> RiskAssessmentResult:
        """Evaluates live checkpoint telemetry using single-forward-pass Bayesian inference."""
        if not self.is_fitted:
            self._fit_context()

        X_query = telemetry.to_array()

        # Posterior probability prediction from TabPFNClassifier
        prob_matrix = self.classifier.predict_proba(X_query)
        # Class 1 is hazard
        if prob_matrix.shape[1] > 1:
            hazard_prob = float(prob_matrix[0, 1])
        else:
            hazard_prob = float(prob_matrix[0, 0])

        # Regression prediction for expected water deficit
        water_deficit_pred = self.regressor.predict(X_query)
        projected_deficit = float(np.maximum(0.0, water_deficit_pred[0]))

        # Hazard determination
        is_hazard = hazard_prob >= settings.HAZARD_PROBABILITY_THRESHOLD
        hazard_label = 1 if is_hazard else 0

        # Confidence: distance from decision boundary
        confidence = float(np.abs(hazard_prob - 0.5) * 2.0)

        # Actionable field guidance
        if is_hazard:
            if telemetry.water_remaining_ml < 300.0 or projected_deficit > 400.0:
                recommendation = "High dehydration hazard. Halt at next shaded shelter and hydrate."
            else:
                recommendation = "Fatigue spike detected. Extend leg interval by 15 minutes to recover."
        else:
            if hazard_prob > 0.40:
                recommendation = "Approaching caution threshold. Maintain steady cadence."
            else:
                recommendation = "Nominal telemetry. Proceed to next checkpoint."

        return RiskAssessmentResult(
            hazard_probability=round(hazard_prob, 4),
            hazard_label=hazard_label,
            projected_water_deficit_ml=round(projected_deficit, 1),
            is_hazard=is_hazard,
            confidence=round(confidence, 4),
            model_mode="Prior Labs TabPFN Bayesian Foundation Model",
            recommendation=recommendation,
        )
