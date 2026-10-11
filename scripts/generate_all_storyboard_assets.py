#!/usr/bin/env python3
"""Master pipeline to programmatically generate all 3 technical video assets and slides for TrailSafe:
1. TECH VIDEO 4: Prior Labs TabPFN In-Context Attention Architecture (7D feature vector)
   - docs/assets/tabpfn_architecture.png
   - docs/assets/broll_tabpfn_architecture.mp4
2. VIDEO 5: Empirical Benchmark Table Pan (17.9 mL TabPFN vs 34.2 mL Random Forest)
   - docs/assets/tabpfn_benchmark.png
   - docs/assets/broll_benchmark.mp4
3. TECH VIDEO 6: Temporal Durable Execution Architecture & State Persistence
   - docs/assets/temporal_durable_execution.png
   - docs/assets/broll_temporal_execution.mp4
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "generate_tech_video_4_tabpfn.py",
    "generate_video_5_benchmark.py",
    "generate_tech_video_6_temporal.py",
]

def main():
    root = Path(__file__).resolve().parent
    for script_name in SCRIPTS:
        script_path = root / script_name
        print(f"\n==========================================")
        print(f"Running: {script_name}")
        print(f"==========================================")
        subprocess.run([sys.executable, str(script_path)], check=True)
    print("\n✓ All 3 technical storyboard video clips and slides generated successfully in docs/assets/!")

if __name__ == "__main__":
    main()
