# TrailSafe: Cinematic B-Roll & Visual Cutaway Storyboard 🎬

> **Audio Status**: Your ElevenLabs voiceover transcript remains **100% UNCHANGED**.  
> **Total Runtime**: ~105 Seconds.  
> **Format**: 16:9 / 1080p60.  
> **Editing Software**: Any editor (CapCut, DaVinci Resolve, Premiere, iMovie, or Loom stitcher).

---

## 🎥 1080p MP4 Video Assets In This Repository Ready for Cutaways

All these 1080p MP4 video files and slides are programmatically rendered and saved inside `docs/assets/` ready to drop directly into your video timeline:
1. `docs/assets/broll_western_ghats_real.mp4` (6s, 1080p) — Authentic video footage of the lush Western Ghats mountain canopy.
2. `docs/assets/broll_no_service.mp4` (6s, 1080p) — Cinematic camera push on a smartphone displaying "NO SERVICE" over the foggy mountain ridge.
3. `docs/assets/broll_screen_zero_backpack.mp4` (6s, 1080p) — Phone zipped into backpack strap pouch on a forest trail for Screen-Zero hiking.
4. `docs/assets/broll_tabpfn_architecture.mp4` (12s, 1080p) — 7D feature vector entering TabPFN in-context attention context with single forward pass Bayesian inference (`tabpfn_architecture.png`).
5. `docs/assets/broll_benchmark.mp4` (12s, 1080p) — Dynamic camera tracking pan across empirical benchmark table highlighting the 17.9 mL error vs 34.2 mL Random Forest metric (`tabpfn_benchmark.png`).
6. `docs/assets/broll_temporal_execution.mp4` (10s, 1080p) — Temporal durable execution engine and state persistence surviving phone reboots without state loss (`temporal_durable_execution.png`).
7. `docs/assets/broll_rescue_hud.mp4` (8s, 1080p) — Tactical search & rescue topographic satellite HUD with blinking SOS beacon at `15.08920, 74.21540`.

---

## ⏱️ Frame-by-Frame Cutaway Storyboard (Drop MP4s Directly by Timestamp)

| Time | Exact Voiceover (ElevenLabs) | What's On Screen (Video Clip) | Exact File to Drag & Drop |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:06** | *"When you hike deep into the Western Ghats or any remote mountain trail, cell service drops to zero."* | **VIDEO 1**: Real drone/scenic footage of the Western Ghats canopy fading into the "NO SERVICE" phone screen. | [`docs/assets/broll_western_ghats_real.mp4`](./assets/broll_western_ghats_real.mp4) ➔ [`docs/assets/broll_no_service.mp4`](./assets/broll_no_service.mp4) |
| **0:06 – 0:12** | *"Standard outdoor apps force you to stare at screens, but when accidents happen solo, nobody even knows you are missing until days later."* | **VIDEO 2**: Quick screen capture of standard turn-by-turn navigation or notification clutter being locked/swiped away. | Quick screen capture of your phone lock screen or stock clip. |
| **0:12 – 0:18** | *"This is TrailSafe: an offline-first dead-man's switch and physiological risk engine built for the Touch Grass challenge."* | **A-ROLL UI**: TrailSafe mobile app screen recording (`http://localhost:8000`). Tap *"Start Hike Session"* (Netravali Ridge). | Screen recording of `http://localhost:8000`. |
| **0:18 – 0:24** | *"The design philosophy is Screen-Zero. You select your trail, zip your phone inside your backpack, and touch grass completely uninterrupted."* | **B-ROLL 3**: Video clip of phone being zipped into backpack strap pouch on a forest trail. Hiker walks forward hands-free. | [`docs/assets/broll_screen_zero_backpack.mp4`](./assets/broll_screen_zero_backpack.mp4) |
| **0:24 – 0:30** | *"When you reach a checkpoint, you give the phone a single tap."* | **A-ROLL UI**: Quick 5-second checkpoint check-in tap on TrailSafe screen: checkmark appears. | Screen recording of `http://localhost:8000`. |
| **0:30 – 0:42** | *"Behind the scenes, we evaluate hiker fatigue and dehydration using Prior Labs Tab-P-F-N foundation models. Hiker distress is a small-sample tabular problem where standard neural networks quickly overfit. Tab-P-F-N ingests historical trail priors and performs in-context Bayesian inference in a single forward pass, with zero training loops and zero hyperparameter tuning."* | **TECH VIDEO 4**: Quick cutaway slide / diagram showing the 7D feature vector entering TabPFN attention context. | [`docs/assets/broll_tabpfn_architecture.mp4`](./assets/broll_tabpfn_architecture.mp4)<br>*(or Slide: [`docs/assets/tabpfn_architecture.png`](./assets/tabpfn_architecture.png))* |
| **0:42 – 0:54** | *"In our empirical benchmarks, Tab-P-F-N forecasted fluid deficit with an error of just 17.9 milliliters, outperforming Random Forest by more than two times zero-shot."* | **VIDEO 5**: Camera tracking pan across the benchmark table highlighting the 17.9 mL error vs 34.2 mL Random Forest metric. | [`docs/assets/broll_benchmark.mp4`](./assets/broll_benchmark.mp4)<br>*(or Slide: [`docs/assets/tabpfn_benchmark.png`](./assets/tabpfn_benchmark.png))* |
| **0:54 – 1:04** | *"To orchestrate the safety countdown, we use Temporal durable execution. A dead-man's switch built with basic sleep timers or cron jobs is fragile. If the app restarts or the phone sleeps, the timer is lost."* | **TECH VIDEO 6**: Architecture flow showing Temporal's durable execution engine and state persistence surviving reboots. | [`docs/assets/broll_temporal_execution.mp4`](./assets/broll_temporal_execution.mp4)<br>*(or Slide: [`docs/assets/temporal_durable_execution.png`](./assets/temporal_durable_execution.png))* |
| **1:04 – 1:12** | *"With Temporal, the workflow is entirely durable. Every checkpoint signal, timer deadline, and window extension survives reboots."* | **TERMINAL VIDEO 7**: Real terminal footage running `simulate_emergency.py` showing ASCII timer progress bar and durable checkpoint resets. | [`docs/assets/broll_terminal_simulation_durable.mp4`](./assets/broll_terminal_simulation_durable.mp4) |
| **1:12 – 1:18** | *"If a hiker misses a waypoint, Temporal triggers a ten-minute safety grace period before sounding a loud acoustic rescue siren..."* | **SIMULATION VIDEO 8**: Real terminal footage showing dead-man switch timeout, red pulsing HUD, acoustic alarm countdown, and emergency dispatch. | [`docs/assets/broll_terminal_simulation_emergency.mp4`](./assets/broll_terminal_simulation_emergency.mp4) |
| **1:18 – 1:26** | *"...and escalating to emergency dispatch."* | **VIDEO 9**: Tactical search-and-rescue satellite GIS HUD with blinking SOS beacon at `15.08920, 74.21540`. | [`docs/assets/broll_rescue_hud.mp4`](./assets/broll_rescue_hud.mp4) |
| **1:26 – 1:36** | *"When triggered, TrailSafe transmits an instant rescue payload over Telegram and Twilio S-M-S with exact G-P-S coordinates and Tab-P-F-N diagnostic telemetry."* | **PHONE PROOF 10**: Screen recording or screenshot of the real Telegram rescue alert from `@ktcl_commuteshield_bot` with Google Maps pin. | [`docs/assets/telegram_alert_screenshot.png`](./assets/telegram_alert_screenshot.png) |
| **1:36 – 1:41** | *"Tested with Temporal's in-memory time-skipping test server and verified green in GitHub Actions C-I..."* | **CI PROOF 11**: Split cut of terminal running `pytest` (10 passed in 1.42s) and the green `TrailSafe CI ✓` passing badge with rolling test odometer. | [`docs/assets/broll_ci_proof_pytest.mp4`](./assets/broll_ci_proof_pytest.mp4)<br>*(or Slide: [`docs/assets/ci_proof_pytest.png`](./assets/ci_proof_pytest.png))* |
| **1:41 – 1:45** | *"...TrailSafe is fully open source under the MIT license to protect solo explorers everywhere. Go outside, stay safe, and touch grass."* | **CLOSING HERO 12**: GitHub repository screen (`github.com/Labreo/trailsafe`), fading into scenic Western Ghats mountain ridge with *"TrailSafe — Touch Grass Safely"*. | [`docs/assets/broll_closing_hero.mp4`](./assets/broll_closing_hero.mp4)<br>*(or Slide: [`docs/assets/closing_hero.png`](./assets/closing_hero.png))* |

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
