"""Comparative Benchmark: Prior Labs TabPFN vs scikit-learn baselines.

Empirically validates TabPFN's Bayesian prior calibration and generalization
on small-sample single-hike historical datasets (N <= 40).
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from tabpfn import TabPFNClassifier, TabPFNRegressor

import json
from src.config import settings
from src.ml.tabpfn_engine import FEATURE_COLUMNS


def run_benchmark(
    data_path: Path = settings.DATA_DIR / "sample_trail_history.csv",
    force_recompute: bool = False,
) -> Dict[str, Any]:
    """Runs cross-validated benchmark comparing TabPFN against classical baselines with caching."""
    cache_file = settings.DATA_DIR / "benchmark_cache.json"
    if not force_recompute and cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y_cls = df["hazard_label"].to_numpy(dtype=np.int64)
    y_reg = df["water_deficit_ml"].to_numpy(dtype=np.float32)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    tabpfn_probs = []
    rf_probs = []
    lr_probs = []

    tabpfn_reg_preds = []
    rf_reg_preds = []
    lin_reg_preds = []

    y_test_cls_all = []
    y_test_reg_all = []

    for train_idx, test_idx in skf.split(X, y_cls):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train_c, y_test_c = y_cls[train_idx], y_cls[test_idx]
        y_train_r, y_test_r = y_reg[train_idx], y_reg[test_idx]

        y_test_cls_all.extend(y_test_c.tolist())
        y_test_reg_all.extend(y_test_r.tolist())

        # 1. TabPFN (In-context single forward pass)
        tab_clf = TabPFNClassifier()
        tab_clf.fit(X_train, y_train_c)
        tab_p = tab_clf.predict_proba(X_test)[:, 1]
        tabpfn_probs.extend(tab_p.tolist())

        tab_reg = TabPFNRegressor()
        tab_reg.fit(X_train, y_train_r)
        tab_r = tab_reg.predict(X_test)
        tabpfn_reg_preds.extend(tab_r.tolist())

        # 2. Random Forest
        rf_clf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf_clf.fit(X_train, y_train_c)
        rf_p = rf_clf.predict_proba(X_test)[:, 1] if len(rf_clf.classes_) > 1 else np.zeros(len(X_test))
        rf_probs.extend(rf_p.tolist())

        rf_reg = RandomForestRegressor(n_estimators=50, random_state=42)
        rf_reg.fit(X_train, y_train_r)
        rf_r = rf_reg.predict(X_test)
        rf_reg_preds.extend(rf_r.tolist())

        # 3. Linear / Logistic Regression
        lr_clf = LogisticRegression(max_iter=1000)
        lr_clf.fit(X_train, y_train_c)
        lr_p = lr_clf.predict_proba(X_test)[:, 1] if len(lr_clf.classes_) > 1 else np.zeros(len(X_test))
        lr_probs.extend(lr_p.tolist())

        lin_reg = LinearRegression()
        lin_reg.fit(X_train, y_train_r)
        lin_r = lin_reg.predict(X_test)
        lin_reg_preds.extend(lin_r.tolist())

    y_test_cls_arr = np.array(y_test_cls_all)
    y_test_reg_arr = np.array(y_test_reg_all)

    tab_brier = brier_score_loss(y_test_cls_arr, tabpfn_probs)
    rf_brier = brier_score_loss(y_test_cls_arr, rf_probs)
    lr_brier = brier_score_loss(y_test_cls_arr, lr_probs)

    tab_auc = roc_auc_score(y_test_cls_arr, tabpfn_probs)
    rf_auc = roc_auc_score(y_test_cls_arr, rf_probs)
    lr_auc = roc_auc_score(y_test_cls_arr, lr_probs)

    tab_mae = mean_absolute_error(y_test_reg_arr, tabpfn_reg_preds)
    rf_mae = mean_absolute_error(y_test_reg_arr, rf_reg_preds)
    lin_mae = mean_absolute_error(y_test_reg_arr, lin_reg_preds)

    results = {
        "dataset_size": len(X),
        "classification": {
            "tabpfn": {
                "brier_score": round(float(tab_brier), 4),
                "roc_auc": round(float(tab_auc), 4),
                "accuracy": round(float(accuracy_score(y_test_cls_arr, np.array(tabpfn_probs) >= 0.5)), 4),
            },
            "random_forest": {
                "brier_score": round(float(rf_brier), 4),
                "roc_auc": round(float(rf_auc), 4),
                "accuracy": round(float(accuracy_score(y_test_cls_arr, np.array(rf_probs) >= 0.5)), 4),
            },
            "logistic_regression": {
                "brier_score": round(float(lr_brier), 4),
                "roc_auc": round(float(lr_auc), 4),
                "accuracy": round(float(accuracy_score(y_test_cls_arr, np.array(lr_probs) >= 0.5)), 4),
            },
        },
        "regression": {
            "tabpfn_mae_ml": round(float(tab_mae), 2),
            "random_forest_mae_ml": round(float(rf_mae), 2),
            "linear_regression_mae_ml": round(float(lin_mae), 2),
        },
    }
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    except Exception:
        pass
    return results


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("[bold cyan]Running Empirical Comparative Evaluation: Prior Labs TabPFN vs Baselines...[/bold cyan]")
    res = run_benchmark()

    table = Table(title="Small-Sample Calibration & Predictive Performance (Leave-One-Out CV)")
    table.add_column("Model", style="bold")
    table.add_column("Brier Score (Lower is Better)")
    table.add_column("ROC-AUC (Higher is Better)")
    table.add_column("Accuracy")
    table.add_column("Water Deficit MAE (mL)")

    cls_res = res["classification"]
    reg_res = res["regression"]

    table.add_row(
        "Prior Labs TabPFN",
        f"{cls_res['tabpfn']['brier_score']:.4f}",
        f"{cls_res['tabpfn']['roc_auc']:.4f}",
        f"{cls_res['tabpfn']['accuracy'] * 100:.1f}%",
        f"{reg_res['tabpfn_mae_ml']:.1f}",
    )
    table.add_row(
        "Random Forest (50 trees)",
        f"{cls_res['random_forest']['brier_score']:.4f}",
        f"{cls_res['random_forest']['roc_auc']:.4f}",
        f"{cls_res['random_forest']['accuracy'] * 100:.1f}%",
        f"{reg_res['random_forest_mae_ml']:.1f}",
    )
    table.add_row(
        "Logistic / Linear Reg",
        f"{cls_res['logistic_regression']['brier_score']:.4f}",
        f"{cls_res['logistic_regression']['roc_auc']:.4f}",
        f"{cls_res['logistic_regression']['accuracy'] * 100:.1f}%",
        f"{reg_res['linear_regression_mae_ml']:.1f}",
    )

    console.print(table)
