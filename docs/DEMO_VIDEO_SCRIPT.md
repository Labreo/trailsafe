# TrailSafe: 2-Minute Championship Demo Video Runbook 🎥

> **Target Duration**: 105 seconds (1m 45s) — Safe buffer beneath the 120s limit.  
> **Platform/Tool**: Use **Loom**, **QuickTime Screen Recording**, or **OBS Studio** at 1080p.  
> **Audio**: Speak naturally into your microphone or record voiceover over the screen capture.

---

## Pre-Recording Checklist (30 Seconds Setup)

1. Open **Browser Tab 1**: `http://localhost:8000` (run `python3 -m uvicorn src.server.app:app --port 8000` or open in mobile viewport devtools `Cmd+Shift+M`).
2. Open **Terminal Window**: In repo directory `/Users/sanjaywaradkar/trailsafe`.
3. Open **Telegram Web or Phone**: Chat with `@ktcl_commuteshield_bot` showing the rescue alert.

---

## 🎬 Scene-by-Scene Script & Action Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENE 1: The Hook & Screen-Zero Philosophy (0:00 - 0:25)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ ON SCREEN:                                                                  │
│ • Browser open at http://localhost:8000 (Mobile field app).                │
│ • Click "Start Hike Session" (Route: Netravali Ridge, 45 min interval).     │
│                                                                             │
│ NARRATION (Voiceover):                                                      │
│ "When you hike deep into the Western Ghats or any mountain trail, cell      │
│  service drops to zero. Standard outdoor apps force you to stare at screens,│
│  but when accidents happen solo, no one knows you're missing for days.      │
│  This is TrailSafe: an offline-first dead-man's switch and tabular risk      │
│  engine built for the Touch Grass challenge. You set your trail, zip your   │
│  phone in your backpack, and touch grass—uninterrupted."                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENE 2: Prior Labs TabPFN Bayesian Foundation Model (0:25 - 0:55)          │
├─────────────────────────────────────────────────────────────────────────────┤
│ ON SCREEN:                                                                  │
│ • In UI: Tap "Check-in at Waypoint 1". Show TabPFN Bayesian Risk: 8.2% and  │
│   Projected Fluid Deficit: 0 mL.                                            │
│ • Split-screen or switch to Terminal and run:                               │
│   python3 src/ml/benchmark_eval.py                                          │
│   (Highlight the summary table showing TabPFN beating Random Forest).       │
│                                                                             │
│ NARRATION (Voiceover):                                                      │
│ "Hiker distress is a small-sample tabular problem where standard neural     │
│  networks overfit. We use Prior Labs TabPFN foundation models.              │
│  TabPFN treats historical trail priors as an in-context learning problem,   │
│  generating calibrated Bayesian risk probabilities in a single forward pass │
│  with zero training loops or hyperparameters.                               │
│  In our empirical benchmark, TabPFN predicted hydration deficit with an     │
│  MAE of just 17.9 mL, outperforming Random Forest by more than 2x."         │
└─────────────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENE 3: Temporal Durable Execution & Dead-Man Switch (0:55 - 1:25)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ ON SCREEN:                                                                  │
│ • Terminal: Run the automated simulation:                                   │
│   python3 scripts/simulate_emergency.py                                     │
│ • Show the ASCII banner, countdown progress bar, TabPFN telemetry loading,  │
│   and the transition into GRACE_PERIOD when a waypoint is missed.          │
│                                                                             │
│ NARRATION (Voiceover):                                                      │
│ "A dead-man's switch built with standard sleep timers or cron jobs is       │
│  fragile—if the app restarts or the phone sleeps, the timer is lost.        │
│  With Temporal, the safety workflow is 100% durable. Every signal, timer,   │
│  and window extension survives reboots. If a hiker misses a waypoint,       │
│  Temporal enters a 10-minute safety grace period before sounding an acoustic│
│  siren and escalating to remote rescue dispatch."                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCENE 4: Real Multi-Channel Dispatch & CI Proof (1:25 - 1:45)               │
├─────────────────────────────────────────────────────────────────────────────┤
│ ON SCREEN:                                                                  │
│ • Show Telegram alert from @ktcl_commuteshield_bot with GPS pin:            │
│   'TRAILSAFE RESCUE ALERT: Coordinates 15.08920, 74.21540 (Google Maps)'.   │
│ • Switch to Terminal and run:                                               │
│   pytest                                                                    │
│   (Highlight: '10 passed in 100% coverage' & GitHub Actions CI green badge).│
│                                                                             │
│ NARRATION (Voiceover):                                                      │
│ "When triggered, TrailSafe transmits an instant emergency dispatch over     │
│  Telegram and Twilio SMS with live Google Maps coordinates and TabPFN       │
│  physiological diagnostics.                                                 │
│  Tested with Temporal's in-memory time-skipping test server and 100% green  │
│  in GitHub Actions CI. TrailSafe is fully open source under the MIT license │
│  to keep solo hikers safe while touching grass. Thank you!"                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Quick Tips for Maximum Impact

1. **Keep Terminal Text Large**: Press `Cmd + +` in Terminal so text is crystal clear on 1080p.
2. **Show, Don't Read**: Don't linger on slides or static text. Keep things moving across the three screens: **Web App ➔ Terminal Benchmark ➔ Telegram Alert**.
3. **Upload to YouTube or Loom**:
   * Set title: `TrailSafe: Offline Solo Hiker Dead-Man's Switch (TabPFN + Temporal)`
   * Copy the URL or ID into [`docs/SUBMISSION_POST.md`](./SUBMISSION_POST.md).
