# TrailSafe: Cinematic B-Roll & Visual Cutaway Storyboard 🎬

> **Audio Status**: Your ElevenLabs voiceover transcript remains **100% UNCHANGED**.  
> **Total Runtime**: ~105 Seconds.  
> **Format**: 16:9 / 1080p60.  
> **Editing Software**: Any editor (CapCut, DaVinci Resolve, Premiere, iMovie, or Loom stitcher).

---

## 🎨 Visual Assets In This Repository Ready for Cutaways

All these high-resolution 16:9 visuals are already saved inside `docs/assets/`:
1. `docs/assets/broll_no_service.png` — Misty Western Ghats ridge with hiker holding phone showing "NO SERVICE".
2. `docs/assets/broll_rescue_hud.png` — Tactical topographic GIS rescue HUD with blinking SOS coordinate readout (`15.08920, 74.21540`).
3. `docs/assets/tabpfn_benchmark.png` — Scientific analytics benchmark comparing TabPFN vs Random Forest.
4. `docs/assets/trailsafe_hero.png` — Tactical dark-slate mobile app mockup.

---

## ⏱️ Frame-by-Frame Cutaway Storyboard

| Time | Exact Voiceover (ElevenLabs) | Visual Cutaway (What's On Screen) | Cut Type & Notes |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:06** | *"When you hike deep into the Western Ghats or any remote mountain trail, cell service drops to zero."* | **B-ROLL CUTAWAY 1**:<br>Display [`docs/assets/broll_no_service.png`](./assets/broll_no_service.png) (or 4s stock video of foggy mountains). Subtle slow push-in zoom. | **Slow Zoom**: Sets a cinematic, real-world outdoor atmosphere immediately. |
| **0:06 – 0:12** | *"Standard outdoor apps force you to stare at screens, but when accidents happen solo, nobody even knows you are missing until days later."* | **B-ROLL CUTAWAY 2**:<br>Close-up of a regular smartphone screen overflowing with confusing maps, social feeds, and notifications getting locked/swiped away. | **Quick Cut**: Contrast modern screen fatigue with isolation danger. |
| **0:12 – 0:18** | *"This is TrailSafe: an offline-first dead-man's switch and physiological risk engine built for the Touch Grass challenge."* | **A-ROLL UI**:<br>Full screen capture of TrailSafe mobile app running at `http://localhost:8000`. Quick tap on *"Start Hike Session"* (Route: Netravali Ridge). | **UI Screen**: Clean, responsive, high-contrast dark theme. |
| **0:18 – 0:24** | *"The design philosophy is Screen-Zero. You select your trail, zip your phone inside your backpack, and touch grass completely uninterrupted."* | **B-ROLL CUTAWAY 3**:<br>Phone being slipped and zipped into a backpack shoulder pocket. Hiker walking down a trail with hands free, looking up at the trees. | **Metaphor Cut**: The visual embodiment of **"Screen-Zero" & "Touching Grass"**. |
| **0:24 – 0:30** | *"When you reach a checkpoint, you give the phone a single tap."* | **A-ROLL UI**:<br>Quick cut back to TrailSafe screen: single tap on *"Check-in at Waypoint 1"*. Checkmark appears. | **Action**: Shows the 5-second micro-interaction. |
| **0:30 – 0:42** | *"Behind the scenes, we evaluate hiker fatigue and dehydration using Prior Labs Tab-P-F-N foundation models. Hiker distress is a small-sample tabular problem where standard neural networks quickly overfit. Tab-P-F-N ingests historical trail priors and performs in-context Bayesian inference in a single forward pass, with zero training loops and zero hyperparameter tuning."* | **TECH CUTAWAY 4**:<br>Motion diagram or slide showing the 7D feature vector (`[elevation, pace, elapsed_time, temp, water, cadence, roughness]`) passing through TabPFN attention architecture. Flash model signature: *"Prior Labs TabPFN Bayesian Foundation Model"*. | **Architecture**: Proves deep, authentic use of Prior Labs tabular foundation models. |
| **0:42 – 0:54** | *"In our empirical benchmarks, Tab-P-F-N forecasted fluid deficit with an error of just 17.9 milliliters, outperforming Random Forest by more than two times zero-shot."* | **BENCHMARK CUTAWAY 5**:<br>Cut to [`docs/assets/tabpfn_benchmark.png`](./assets/tabpfn_benchmark.png) OR Terminal running `python3 src/ml/benchmark_eval.py`. Highlight the **17.9 mL error vs 34.2 mL Random Forest** metric. | **Empirical Proof**: Hard scientific evidence of superiority. |
| **0:54 – 1:04** | *"To orchestrate the safety countdown, we use Temporal durable execution. A dead-man's switch built with basic sleep timers or cron jobs is fragile. If the app restarts or the phone sleeps, the timer is lost."* | **TECH CUTAWAY 6**:<br>Clean architecture diagram showing the durable state machine: `wait_condition()`, dynamic signals (`check_in`, `extend_window`), and persistent state history. | **Engineering Depth**: Explains why Temporal was necessary instead of a trivial timer. |
| **1:04 – 1:12** | *"With Temporal, the workflow is entirely durable. Every checkpoint signal, timer deadline, and window extension survives reboots."* | **TERMINAL A-ROLL**:<br>Terminal capture running `python3 scripts/simulate_emergency.py` showing the ASCII countdown bar and live state persistence. | **Live Motion**: Terminal action proves live execution. |
| **1:12 – 1:18** | *"If a hiker misses a waypoint, Temporal triggers a ten-minute safety grace period before sounding a loud acoustic rescue siren..."* | **SIMULATION CUTAWAY 7**:<br>Terminal flashes yellow: `⚠️ CHECKPOINT TIMEOUT -> ENTERING GRACE_PERIOD (10 MIN)`. Mobile web app sounds acoustic siren pulsing red. | **Tension / Climax**: Shows the safety net in action. |
| **1:18 – 1:26** | *"...and escalating to emergency dispatch."* | **B-ROLL CUTAWAY 8**:<br>Cut to tactical topographic satellite HUD [`docs/assets/broll_rescue_hud.png`](./assets/broll_rescue_hud.png) showing the blinking red emergency beacon at coordinates `15.08920, 74.21540`. | **Search & Rescue Aesthetic**: Elevates the project to real-world mission critical. |
| **1:26 – 1:36** | *"When triggered, TrailSafe transmits an instant rescue payload over Telegram and Twilio S-M-S with exact G-P-S coordinates and Tab-P-F-N diagnostic telemetry."* | **DELIVERY PROOF CUTAWAY 9**:<br>Smartphone / Telegram Web screen showing the live Telegram rescue message from `@ktcl_commuteshield_bot` with the Google Maps pin. | **Physical Delivery Proof**: Demonstrates real end-to-end integration. |
| **1:36 – 1:41** | *"Tested with Temporal's in-memory time-skipping test server and verified green in GitHub Actions C-I..."* | **CI PROOF CUTAWAY 10**:<br>Quick split cut showing `pytest` running `10 passed in 18s` alongside the green GitHub Actions `TrailSafe CI ✓` status badge. | **Quality Assurance**: Proves production engineering discipline. |
| **1:41 – 1:45** | *"...TrailSafe is fully open source under the MIT license to protect solo explorers everywhere. Go outside, stay safe, and touch grass."* | **CLOSING HERO CUTAWAY 11**:<br>GitHub repository card (`github.com/Labreo/trailsafe`), fading out to the misty mountain ridge with title card: *"TrailSafe — Built for Hacktoberfest 2026."* | **Call to Action**: High emotional payoff on the "Touch Grass" theme. |

---

## 💡 Quick Tips for Easy Editing (No Video Editing Experience Needed)

1. **Free Video Stock Clips (Optional 5s Clips)**:
   * If you want live video clips instead of still photos for the mountain or backpack, search Pexels.com (100% free) for:
     * *"Hiker walking forest"*
     * *"Backpack zip"*
2. **Ken Burns Zoom Effect**:
   * For the still images (`broll_no_service.png`, `tabpfn_benchmark.png`, `broll_rescue_hud.png`), apply a simple **105% slow zoom-in** in CapCut, Premiere, or iMovie. It makes still images look like animated documentary footage!
3. **Audio Lock**:
   * Drop your ElevenLabs audio track into the timeline first, and simply place the video cuts to match the table timestamps above!
