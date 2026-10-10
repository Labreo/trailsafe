# TrailSafe: 2-Minute Demo & Video Walkthrough Guide

Use this script and step-by-step walkthrough to record a fast, compelling 1-to-2 minute screen recording (or YouTube demo) for your DEV.to submission.

---

## 🎬 2-Minute Video Script

### Segment 1: The Problem (0:00 - 0:25)
* **What to Show**: You on video or a title card showing a trail photo from the Western Ghats (or mountain trail) with your phone showing `No Service`.
* **Voiceover**:
  > *"When you're hiking solo deep in the backcountry, cellular service vanishes. If you slip on wet rocks or get dehydrated, nobody knows you're overdue until days later. Today I'm demonstrating **TrailSafe**: an offline-first dead-man's switch powered by Prior Labs TabPFN for tabular risk inference and Temporal for durable execution."*

### Segment 2: Trailhead Setup & Screen-Zero (0:25 - 0:50)
* **What to Show**: Screen recording of `http://localhost:8000` (Mobile viewport).
* **Actions**:
  1. Select route: `Netravali Ridge Trail`.
  2. Enter Hiker Name: `Solo Explorer`.
  3. Set Checkpoint Window: `45 minutes`.
  4. Tap **Initiate Trailhead Session**.
* **Voiceover**:
  > *"TrailSafe follows the Screen-Zero principle: 30 seconds at the trailhead to set your route and emergency contacts, then the phone goes into your pack. You look up at the trail, not down at a screen."*

### Segment 3: Waypoint Check-In & Prior Labs TabPFN (0:50 - 1:20)
* **What to Show**: Active Hike screen showing the tactical countdown timer and live metrics.
* **Actions**:
  1. Show moving pace, cadence, and GPS altitude.
  2. Tap **Transmit Waypoint Check-In** (or show the QR Waypoint Scanner).
  3. Highlight the TabPFN Risk Banner updating:
     - `Prior Labs TabPFN Bayesian Risk: 8.2%`
     - `Projected Fluid Deficit: 0 mL`
     - `Recommendation: Pace nominal. Proceed to target waypoint.`
* **Voiceover**:
  > *"When you hit a waypoint, a 5-second tap ingests your physical biometrics. In a single forward pass, Prior Labs TabPFN computes your Bayesian posterior distress risk and predicts your exact hydration shortfall with 17.9 mL accuracy."*

### Segment 4: Temporal Durable State & Crash Survival (1:20 - 1:45)
* **What to Show**: Split screen of Terminal showing Temporal Worker / CLI and the Web UI.
* **Actions**:
  1. Show window extension (`+15m`) updating the durable timer.
  2. Kill the server (`Ctrl+C`), restart it, and refresh—show that the countdown timer and waypoint progression resume with zero data loss.
* **Voiceover**:
  > *"Behind the scenes, Temporal orchestrates the dead-man countdown. Even if the server crashes or your phone restarts mid-trek, Temporal preserves workflow execution state."*

### Segment 5: Emergency Escalation & Dispatch (1:45 - 2:05)
* **What to Show**: Tap **Emergency SOS Panic Trigger** (or let the grace period expire).
* **Actions**:
  1. The acoustic rescue siren pulses through speakers.
  2. Switch to Telegram or SMS view showing the live alert with Google Maps coordinates and TabPFN physiological diagnostics.
* **Voiceover**:
  > *"If you trigger an SOS or miss a checkpoint past the grace period, TrailSafe sounds an audible rescue siren and delivers verified emergency dispatch with your exact GPS coordinates and health metrics. TrailSafe keeps solo hikers safe while letting them truly touch grass."*

---

## 📸 Key Screenshots to Take for DEV.to

1. **`trailsafe_hero.png`**: Mobile view of Trailhead Configuration and Tactical Countdown timer.
2. **`tabpfn_benchmark.png`**: The comparative evaluation table from `src/ml/benchmark_eval.py` showing TabPFN outperforming Random Forest by 2x.
3. **`telegram_alert.png`**: The received rescue alert on Telegram showing GPS coordinates, TabPFN risk score, and Google Maps link.
4. **`temporal_test_suite.png`**: Terminal screenshot showing `pytest` running the 10 automated test cases with Temporal time-skipping.
