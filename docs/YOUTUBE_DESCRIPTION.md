# TrailSafe — YouTube Video Description

When cell signal drops to zero, how do you stay safe on solo wilderness treks?

TrailSafe is an offline-first, Screen-Zero autonomous search-and-rescue dead-man's switch powered by Prior Labs TabPFN foundation models and Temporal durable execution. Engineered for solo hikers, trail runners, and outdoor explorers in cellular dead zones like the Western Ghats.

Built for the DEV Hacktoberfest 2026 Open-Source AI Challenge (Week 1: Touch Grass).

---

### ⏱️ Video Chapters & Timestamps
0:00 - The Backcountry Problem (Western Ghats Cellular Dead Zones)  
0:24 - Screen-Zero Philosophy & Checkpoint Configuration  
0:42 - Prior Labs TabPFN: In-Context Bayesian Inference  
0:54 - Empirical Benchmark: TabPFN vs Random Forest (17.9 mL MAE)  
1:04 - Temporal Durable Execution & Fault-Tolerant State  
1:26 - Search-and-Rescue Dispatch: Live GPS & Telegram Alerts  
1:41 - 100% Open Source (MIT) & Closing Hero  

---

### 🔗 Project Links & Resources
* 📦 GitHub Repository: https://github.com/Labreo/trailsafe
* 📝 Dev.to Submission Post: https://dev.to/challenges/hacktoberfest-week1-2026-10-05
* 🧠 Prior Labs TabPFN: https://priorlabs.ai
* ⏳ Temporal.io: https://temporal.io
* 📄 Full Storyboard & Architecture: https://github.com/Labreo/trailsafe/blob/main/docs/DEMO_VIDEO_STORYBOARD.md

---

### 🌟 Why Open-Source AI Matters on the Trail
Standard outdoor applications demand continuous screen time: live maps, turn-by-turn prompts, and leaderboards. TrailSafe is engineered around "Screen-Zero":
1. Configure your route and check-in window at the trailhead (30 seconds).
2. Slip the phone into your backpack and experience nature uninterrupted.
3. Tap your phone once at physical landmarks.
4. If you miss a checkpoint and grace period, Temporal automatically triggers search-and-rescue dispatch with last-known GPS coordinates, elevation, battery level, and TabPFN physiological deficit forecasts.

---

### 📊 Benchmark Highlights
Evaluating physical distress is a small-sample tabular problem where standard neural networks quickly overfit. TabPFN ingests historical trail priors and performs in-context Bayesian inference in a single forward pass:
* Fluid Deficit Prediction Error: 17.9 mL MAE (TabPFN) vs 34.2 mL (Random Forest) — more than 2x error reduction zero-shot!
* Posterior Inference Latency: < 100ms on consumer laptop/mobile CPU.
* Zero gradient loops, zero hyperparameter tuning, and zero cloud API connectivity.

---

### 🚀 Quickstart (Run Locally)
```bash
git clone https://github.com/Labreo/trailsafe.git
cd trailsafe
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the 100% passing test suite
pytest

# Run the empirical TabPFN benchmark
python3 src/ml/benchmark_eval.py

# Launch the field web app
python3 -m uvicorn src.server.app:app --host 0.0.0.0 --port 8000
```

---

### 🏷️ Tags & Categories
#Hacktoberfest #OpenSourceAI #TabPFN #Temporal #OutdoorSafety #MachineLearning #Python #BayesianInference #HikingSafety #TouchGrass
