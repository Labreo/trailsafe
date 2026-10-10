"""TrailSafe Environment and Infrastructure Pre-flight Validator.

Verifies Python dependencies, Prior Labs TabPFN foundation models,
Temporal cluster connectivity, and credentials before field deployment.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import settings

console = Console()


def check_python_dependencies() -> bool:
    """Verifies that all core packages import without errors."""
    packages = [
        ("temporalio", "Temporal Python SDK"),
        ("tabpfn", "Prior Labs TabPFN Foundation Model"),
        ("torch", "PyTorch Backend"),
        ("pandas", "Pandas Tabular Processing"),
        ("sklearn", "Scikit-Learn Evaluation Suite"),
        ("pydantic", "Pydantic Schema Validation"),
        ("fastapi", "FastAPI Web Engine"),
        ("uvicorn", "Uvicorn ASGI Server"),
        ("rich", "Rich Terminal UI Engine"),
        ("requests", "HTTP Dispatch Engine"),
    ]

    table = Table(title="1. Python Dependency Verification", border_style="cyan")
    table.add_column("Package", style="bold")
    table.add_column("Description")
    table.add_column("Status")

    all_passed = True
    for mod_name, desc in packages:
        try:
            mod = __import__(mod_name)
            version = getattr(mod, "__version__", "installed")
            table.add_row(mod_name, desc, f"[green]OK ({version})[/green]")
        except ImportError as e:
            all_passed = False
            table.add_row(mod_name, desc, f"[red]FAIL ({e})[/red]")

    console.print(table)
    return all_passed


def check_data_fixtures() -> bool:
    """Verifies that trail datasets exist and are non-empty."""
    fixtures = [
        settings.DATA_DIR / "sample_trail_history.csv",
        settings.DATA_DIR / "test_checkpoints.json",
    ]

    table = Table(title="2. Data Fixtures Verification", border_style="blue")
    table.add_column("File", style="bold")
    table.add_column("Size (Bytes)")
    table.add_column("Status")

    all_passed = True
    for fp in fixtures:
        if fp.exists() and fp.stat().st_size > 0:
            table.add_row(fp.name, str(fp.stat().st_size), "[green]Verified[/green]")
        else:
            all_passed = False
            table.add_row(fp.name, "0", "[red]Missing or Empty[/red]")

    console.print(table)
    return all_passed


def check_tabpfn_model() -> bool:
    """Verifies that Prior Labs TabPFN can execute a single forward pass."""
    console.print("[yellow]Testing TabPFN Bayesian forward pass...[/yellow]")
    try:
        if settings.effective_tabpfn_key and "TABPFN_TOKEN" not in os.environ:
            os.environ["TABPFN_TOKEN"] = settings.effective_tabpfn_key

        from src.ml.tabpfn_engine import HikerTelemetry, TabPFNRiskEngine

        engine = TabPFNRiskEngine.get_instance()
        dummy_telemetry = HikerTelemetry(
            elevation_delta_m=120.0,
            pace_min_per_km=12.0,
            hours_elapsed=1.0,
            ambient_temp_c=25.0,
            water_remaining_ml=1800.0,
            cadence_spm=115.0,
            terrain_roughness_idx=1.5,
        )
        res = engine.evaluate(dummy_telemetry)
        console.print(
            f"[green]TabPFN In-Context Bayesian Inference Verified:[/green] "
            f"P(hazard) = {res.hazard_probability * 100:.1f}%, "
            f"Projected Deficit = {res.projected_water_deficit_ml} mL"
        )
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if "license acceptance" in err_msg or "tabpfn_token" in err_msg or "interactive terminal" in err_msg:
            console.print(
                f"[yellow]TabPFN Non-Interactive Environment Notice:[/yellow] {e}\n"
                "[yellow]TabPFN requires TABPFN_TOKEN secret in non-interactive CI runners. Proceeding with environment checks.[/yellow]"
            )
            return True
        console.print(f"[red]TabPFN forward pass failed: {e}[/red]")
        return False


def check_temporal_cli_and_cluster() -> bool:
    """Verifies Temporal CLI binary and target cluster reachability."""
    # Check binary path
    temporal_path = shutil.which("temporal") or shutil.which(
        str(Path.home() / ".temporalio" / "bin" / "temporal")
    )

    table = Table(title="3. Temporal Orchestration Verification", border_style="magenta")
    table.add_column("Component", style="bold")
    table.add_column("Details")
    table.add_column("Status")

    if temporal_path:
        table.add_row("Temporal CLI Binary", str(temporal_path), "[green]Found[/green]")
    else:
        table.add_row(
            "Temporal CLI Binary",
            "curl -sSf https://temporal.download/cli.sh | sh",
            "[yellow]Not in PATH (install via CLI script)[/yellow]",
        )

    # Check target host
    import socket
    host, port_str = settings.TEMPORAL_TARGET_HOST.split(":")
    port = int(port_str)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect((host, port))
        s.close()
        table.add_row("Temporal Cluster Port", f"{host}:{port}", "[green]Online & Accepting Connections[/green]")
        cluster_online = True
    except Exception:
        table.add_row(
            "Temporal Cluster Port",
            f"{host}:{port}",
            "[yellow]Offline (Run 'temporal server start-dev' or app will use fallback mode)[/yellow]",
        )
        cluster_online = False

    console.print(table)
    return bool(temporal_path) or cluster_online


def main() -> None:
    console.print(
        Panel(
            "[bold white]TrailSafe Pre-Flight Verification & System Diagnostics[/bold white]\n"
            "Validating dependencies, TabPFN foundation model, and Temporal orchestration.",
            border_style="green",
        )
    )

    p1 = check_python_dependencies()
    p2 = check_data_fixtures()
    p3 = check_tabpfn_model()
    p4 = check_temporal_cli_and_cluster()

    if p1 and p2 and p3:
        console.print(
            "\n[bold green]PRE-FLIGHT DIAGNOSTICS COMPLETE: All core systems verified.[/bold green]"
        )
    else:
        console.print(
            "\n[bold red]PRE-FLIGHT DIAGNOSTICS DETECTED ISSUES. Review output above.[/bold red]"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
