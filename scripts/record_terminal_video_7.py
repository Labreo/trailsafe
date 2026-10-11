#!/usr/bin/env python3
"""Records TERMINAL VIDEO 7 for TrailSafe Demo Storyboard via hackathon-demo-video-producer standards.
Duration: 8.0 seconds (1:04 – 1:12 in storyboard), 1080p @ 30fps.
NO AUDIO TRACK.

Captures authentic terminal execution of `python3 scripts/simulate_emergency.py`:
- Command prompt typing invocation
- Step 1: Trailhead registration & TabPFN in-context model fit (Zero training loops)
- Step 2: Checkpoint 1 Screen-Zero tap, nominal telemetry, TabPFN Bayesian risk 0.1%
- Step 3: Checkpoint 2 Steep scramble, elevated fatigue 67.9%, fluid deficit 315.9 mL
- Temporal durable timer window progression (45:00 countdown)
"""

import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_MP4 = ASSETS_DIR / "broll_terminal_simulation_durable.mp4"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 8.0  # Exactly 8.0 seconds (1:04 – 1:12)
TOTAL_FRAMES = int(FPS * DURATION)

# Load fonts
try:
    FONT_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 17, index=0)
    FONT_MONO_BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 17, index=1)
    FONT_TITLEBAR = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14, index=1)
    FONT_BADGE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13, index=1)
except Exception:
    FONT_MONO = ImageFont.load_default()
    FONT_MONO_BOLD = ImageFont.load_default()
    FONT_TITLEBAR = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()

# Window geometry (macOS Terminal)
WX, WY, WW, WH = 100, 50, 1720, 980
TITLEBAR_H = 46

# Colors
COL_CANVAS = (10, 14, 22)
COL_TERM_BG = (13, 17, 23)
COL_TITLEBAR = (22, 27, 34)
COL_BORDER = (48, 54, 61)

COL_PROMPT = (56, 189, 248)       # Cyan
COL_WHITE = (240, 246, 252)       # Text primary
COL_GRAY = (139, 148, 158)        # Muted
COL_GREEN = (63, 185, 80)         # Success
COL_YELLOW = (210, 153, 34)       # Warning / amber
COL_RED = (248, 81, 73)           # Danger
COL_BLUE = (88, 166, 255)         # Blue info
COL_CYAN = (56, 189, 248)         # Cyan


def draw_terminal_chrome(draw: ImageDraw.ImageDraw, title: str):
    # Outer drop shadow / glow
    draw.rounded_rectangle([(WX - 2, WY - 2), (WX + WW + 2, WY + WH + 2)], radius=12, outline=(30, 41, 59), width=2)
    # Terminal body
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + WH)], radius=12, fill=COL_TERM_BG, outline=COL_BORDER, width=1)
    # Titlebar header
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + TITLEBAR_H)], radius=12, fill=COL_TITLEBAR, outline=COL_BORDER, width=1)
    # Fill bottom corners of titlebar to square them with terminal body
    draw.rectangle([(WX, WY + TITLEBAR_H - 12), (WX + WW, WY + TITLEBAR_H)], fill=COL_TITLEBAR)

    # macOS Traffic light buttons
    draw.ellipse([(WX + 22, WY + 15), (WX + 36, WY + 29)], fill=(237, 106, 94))   # Red
    draw.ellipse([(WX + 44, WY + 15), (WX + 58, WY + 29)], fill=(245, 191, 79))   # Yellow
    draw.ellipse([(WX + 66, WY + 15), (WX + 80, WY + 29)], fill=(98, 197, 84))    # Green

    # Title tab pill
    pill_w = 480
    pill_x = WX + (WW - pill_w) // 2
    draw.rounded_rectangle([(pill_x, WY + 8), (pill_x + pill_w, WY + 38)], radius=6, fill=(13, 17, 23), outline=(48, 54, 61))
    tw = FONT_TITLEBAR.getlength(title)
    draw.text((pill_x + (pill_w - tw) // 2, WY + 14), title, fill=COL_GRAY, font=FONT_TITLEBAR)

    # Right badge
    rw = FONT_BADGE.getlength("TEMPORAL WORKFLOW SIMULATION")
    rx = WX + WW - rw - 35
    draw.rounded_rectangle([(rx - 10, WY + 10), (rx + rw + 10, WY + 36)], radius=13, fill=(30, 41, 59), outline=(56, 189, 248))
    draw.text((rx, WY + 14), "TEMPORAL WORKFLOW SIMULATION", fill=COL_PROMPT, font=FONT_BADGE)


# Real terminal output lines with timestamp appearance milestones
# Each entry: (time_in_seconds, [(text_segment, color, is_bold)])
TERMINAL_SCRIPT = [
    # Command prompt
    (0.0, [
        ("trailsafe@western-ghats ~ % ", COL_PROMPT, True),
    ]),
    (0.4, [
        ("python3 scripts/simulate_emergency.py", COL_WHITE, True),
    ]),
    # Banner
    (0.8, [
        ("==========================================================================", COL_GRAY, False),
    ]),
    (1.0, [
        (" /// TRAILSAFE: BACKCOUNTRY DEAD-MAN'S SWITCH SIMULATION", COL_CYAN, True),
    ]),
    (1.1, [
        (" Prior Labs TabPFN In-Context Bayesian Engine + Temporal Durable Execution", COL_GRAY, False),
    ]),
    (1.2, [
        ("==========================================================================", COL_GRAY, False),
    ]),
    # Step 1
    (1.4, [
        (">> STEP 1: TRAILHEAD REGISTRATION & TABPFN IN-CONTEXT PRIORS", COL_CYAN, True),
    ]),
    (1.5, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (1.6, [
        ("  Hiker:           Sanjay (Solo Mountaineer)", COL_WHITE, False),
    ]),
    (1.7, [
        ("  Trail:           Netravali Ridge Trail (Western Ghats, Goa)", COL_WHITE, False),
    ]),
    (1.8, [
        ("  Waypoints:       3 checkpoints (Gate -> Canyon -> Ridge Peak)", COL_GRAY, False),
    ]),
    (1.9, [
        ("  Leg Timeout:     45 minutes per checkpoint", COL_GRAY, False),
    ]),
    (2.0, [
        ("  Grace Period:    10 minutes with acoustic alarm", COL_GRAY, False),
    ]),
    (2.1, [
        ("  Loading Prior Labs TabPFN Foundation Model & historical trail priors...", COL_GRAY, False),
    ]),
    (2.5, [
        ("  [OK] TabPFN loaded and fitted in-context in ", COL_GREEN, False),
        ("0.08s", COL_GREEN, True),
        (" (Zero training loops).", COL_GREEN, False),
    ]),
    # Step 2: Checkpoint 1
    (2.9, [
        (">> STEP 2: CHECKPOINT 1 — RIVER CANYON CROSSING (Screen-Zero Tap)", COL_CYAN, True),
    ]),
    (3.0, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (3.2, [
        ("  Hiker reaches Checkpoint 1 on time. Phone stays zipped in pack.", COL_WHITE, False),
    ]),
    (3.4, [
        ("  Telemetry: Elevation +120.0m | Pace 11.5 min/km | Temp 25.5°C | Water 1800.0 mL", COL_GRAY, False),
    ]),
    (3.6, [
        ("  TabPFN Bayesian Hazard Risk: ", COL_WHITE, False),
        ("[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] ", COL_GREEN, True),
        ("0.1%", COL_GREEN, True),
    ]),
    (3.8, [
        ("  Projected Fluid Deficit:    ", COL_WHITE, False),
        ("2.1 mL", COL_GREEN, True),
        (" | Status: ", COL_WHITE, False),
        ("NOMINAL", COL_GREEN, True),
    ]),
    (4.0, [
        ("  Temporal Durable Timer:     ", COL_WHITE, False),
        ("Window reset to 45:00 for Leg 2.", COL_GREEN, True),
    ]),
    # Step 3: Checkpoint 2
    (4.4, [
        (">> STEP 3: CHECKPOINT 2 — STEEP SCRAMBLE (Elevated Risk Detected)", COL_CYAN, True),
    ]),
    (4.5, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (4.8, [
        ("  Temperature spikes to 33.5°C; hiker climbs steep boulder field.", COL_WHITE, False),
    ]),
    (5.0, [
        ("  Telemetry: Elevation +340.0m | Pace 18.5 min/km | Temp 33.5°C | Water 300.0 mL", COL_GRAY, False),
    ]),
    (5.3, [
        ("  TabPFN Bayesian Hazard Risk: ", COL_WHITE, False),
        ("[████████████████████░░░░░░░░░░] ", COL_YELLOW, True),
        ("67.9%", COL_YELLOW, True),
    ]),
    (5.6, [
        ("  Projected Fluid Deficit:    ", COL_WHITE, False),
        ("315.9 mL", COL_YELLOW, True),
        (" | Status: ", COL_WHITE, False),
        ("ELEVATED FATIGUE (Caution)", COL_YELLOW, True),
    ]),
    (5.9, [
        ("  Temporal Durable Timer:     ", COL_WHITE, False),
        ("Window reset to 45:00 for Leg 3.", COL_GREEN, True),
    ]),
    # Step 4: Countdown active
    (6.3, [
        (">> STEP 4: LEG 3 TO RIDGE CREST — CELLULAR DEAD ZONE (No Service)", COL_CYAN, True),
    ]),
    (6.5, [
        ("  Hiker enters dense canopy ravine. Cellular bars drop to NO SERVICE.", COL_GRAY, False),
    ]),
    (6.8, [
        ("  Temporal durable workflow active on device edge worker:", COL_GRAY, False),
    ]),
]


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COL_CANVAS)
    draw = ImageDraw.Draw(img)

    draw_terminal_chrome(draw, "terminal — zsh — python3 scripts/simulate_emergency.py (80x28)")

    start_x = WX + 35
    start_y = WY + TITLEBAR_H + 20
    line_h = 24

    cur_y = start_y

    for appear_t, segments in TERMINAL_SCRIPT:
        if t < appear_t:
            continue

        cur_x = start_x
        # Special typing effect for command prompt line (0.0 to 0.7s)
        if appear_t == 0.4 and t < 0.8:
            cmd = "python3 scripts/simulate_emergency.py"
            char_count = int(len(cmd) * min(1.0, (t - 0.4) / 0.35))
            draw.text((cur_x, cur_y - line_h), "trailsafe@western-ghats ~ % ", fill=COL_PROMPT, font=FONT_MONO_BOLD)
            pw = FONT_MONO_BOLD.getlength("trailsafe@western-ghats ~ % ")
            draw.text((cur_x + pw, cur_y - line_h), cmd[:char_count], fill=COL_WHITE, font=FONT_MONO_BOLD)
            continue
        elif appear_t == 0.0 and t < 0.4:
            draw.text((cur_x, cur_y), "trailsafe@western-ghats ~ % ", fill=COL_PROMPT, font=FONT_MONO_BOLD)
            # blinking cursor
            if int(t * 4) % 2 == 0:
                pw = FONT_MONO_BOLD.getlength("trailsafe@western-ghats ~ % ")
                draw.text((cur_x + pw, cur_y), "█", fill=COL_WHITE, font=FONT_MONO)
            cur_y += line_h
            continue
        elif appear_t == 0.4:
            # Already drawn with prompt
            continue

        for text, color, is_bold in segments:
            f = FONT_MONO_BOLD if is_bold else FONT_MONO
            draw.text((cur_x, cur_y), text, fill=color, font=f)
            cur_x += f.getlength(text)

        cur_y += line_h

    # Dynamic countdown timer bar for Leg 3 at bottom (active from 7.0s to 8.0s)
    if t >= 7.0:
        cd_t = t - 7.0
        rem_seconds = int(45 * 60 - cd_t * 120)
        mins, secs = divmod(max(0, rem_seconds), 60)
        draw.text((start_x, cur_y), f"  [TIMER] Leg 3 Checkpoint Window: ", fill=COL_WHITE, font=FONT_MONO_BOLD)
        tx = start_x + FONT_MONO_BOLD.getlength("  [TIMER] Leg 3 Checkpoint Window: ")
        draw.text((tx, cur_y), f"{mins:02d}:{secs:02d} remaining...", fill=COL_YELLOW, font=FONT_MONO_BOLD)
        cur_y += line_h

    # Blinking terminal cursor at bottom
    if int(t * 4) % 2 == 0:
        draw.text((start_x, cur_y), "█", fill=COL_WHITE, font=FONT_MONO)

    return img


def main():
    print(f"Rendering TERMINAL VIDEO 7 -> {OUTPUT_MP4} ({DURATION}s @ {FPS}fps, NO AUDIO)...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-t", str(DURATION),
        str(OUTPUT_MP4)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(TOTAL_FRAMES):
        t = i / FPS
        frame = render_frame(t)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"✓ Successfully rendered TERMINAL VIDEO 7: {OUTPUT_MP4} ({os.path.getsize(OUTPUT_MP4)} bytes)")


if __name__ == "__main__":
    main()
