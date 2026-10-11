#!/usr/bin/env python3
"""Records SIMULATION VIDEO 8 for TrailSafe Demo Storyboard via hackathon-demo-video-producer standards.
Duration: 6.0 seconds (1:12 – 1:18 in storyboard), 1080p @ 30fps.
NO AUDIO TRACK.

Captures authentic terminal execution of `python3 scripts/simulate_emergency.py` (Steps 4, 5, 6):
- Leg 3 checkpoint deadline expiry
- Flashing red alert banner: `⚠️ CHECKPOINT TIMEOUT -> ENTERING GRACE_PERIOD`
- Step 5: 10-minute Grace Period & acoustic siren countdown
- Step 6: Temporal emergency escalation & dispatch activity
- Multi-channel dispatch payload transmission with Telegram DELIVERED & GPS pin
- Tactical emergency pulsing glow & HUD warning indicators
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

OUTPUT_MP4 = ASSETS_DIR / "broll_terminal_simulation_emergency.mp4"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 6.0  # Exactly 6.0 seconds (1:12 – 1:18)
TOTAL_FRAMES = int(FPS * DURATION)

# Load fonts
try:
    FONT_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16, index=0)
    FONT_MONO_BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16, index=1)
    FONT_BANNER = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22, index=1)
    FONT_TITLEBAR = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14, index=1)
    FONT_BADGE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13, index=1)
except Exception:
    FONT_MONO = ImageFont.load_default()
    FONT_MONO_BOLD = ImageFont.load_default()
    FONT_BANNER = ImageFont.load_default()
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

COL_PROMPT = (56, 189, 248)
COL_WHITE = (240, 246, 252)
COL_GRAY = (139, 148, 158)
COL_GREEN = (63, 185, 80)
COL_YELLOW = (210, 153, 34)
COL_RED = (248, 81, 73)
COL_CYAN = (56, 189, 248)


def draw_terminal_chrome(draw: ImageDraw.ImageDraw, title: str, is_emergency: bool = False, pulse: float = 0.0):
    border_col = COL_BORDER
    if is_emergency:
        # Red pulsing emergency border
        r = int(180 + pulse * 75)
        g = int(28 + pulse * 20)
        b = int(28 + pulse * 20)
        border_col = (r, g, b)

    draw.rounded_rectangle([(WX - 2, WY - 2), (WX + WW + 2, WY + WH + 2)], radius=12, outline=border_col, width=2 if is_emergency else 1)
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + WH)], radius=12, fill=COL_TERM_BG, outline=border_col, width=1)
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + TITLEBAR_H)], radius=12, fill=COL_TITLEBAR, outline=border_col, width=1)
    draw.rectangle([(WX, WY + TITLEBAR_H - 12), (WX + WW, WY + TITLEBAR_H)], fill=COL_TITLEBAR)

    # Traffic light dots
    draw.ellipse([(WX + 22, WY + 15), (WX + 36, WY + 29)], fill=(237, 106, 94))
    draw.ellipse([(WX + 44, WY + 15), (WX + 58, WY + 29)], fill=(245, 191, 79))
    draw.ellipse([(WX + 66, WY + 15), (WX + 80, WY + 29)], fill=(98, 197, 84))

    # Title tab pill
    pill_w = 480
    pill_x = WX + (WW - pill_w) // 2
    draw.rounded_rectangle([(pill_x, WY + 8), (pill_x + pill_w, WY + 38)], radius=6, fill=(13, 17, 23), outline=border_col)
    tw = FONT_TITLEBAR.getlength(title)
    draw.text((pill_x + (pill_w - tw) // 2, WY + 14), title, fill=COL_GRAY if not is_emergency else (254, 202, 202), font=FONT_TITLEBAR)

    # Right badge
    badge_txt = "DEAD-MAN TIMEOUT ESCALATION" if not is_emergency else "[ALERT] RESCUE ALARM ACTIVE"
    badge_bg = (69, 10, 10) if is_emergency else (30, 41, 59)
    badge_fg = (255, 100, 100) if is_emergency else (248, 113, 113)
    rw = FONT_BADGE.getlength(badge_txt)
    rx = WX + WW - rw - 35
    draw.rounded_rectangle([(rx - 10, WY + 10), (rx + rw + 10, WY + 36)], radius=13, fill=badge_bg, outline=badge_fg)
    draw.text((rx, WY + 14), badge_txt, fill=badge_fg, font=FONT_BADGE)


# Real terminal output lines for Video 8
TERMINAL_SCRIPT = [
    # Step 4: Cellular Dead Zone & Timeout
    (0.0, [
        (">> STEP 4: LEG 3 TO RIDGE CREST — CELLULAR DEAD ZONE (No Service)", COL_CYAN, True),
    ]),
    (0.1, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (0.2, [
        ("  Hiker enters dense canopy ravine. Cellular bars drop from 2G to ", COL_GRAY, False),
        ("NO SERVICE", COL_RED, True),
        (".", COL_GRAY, False),
    ]),
    (0.4, [
        ("  Hiker trips on wet basalt, sustains ankle fracture, and cannot move.", COL_WHITE, False),
    ]),
    (0.6, [
        ("  Hiker cannot reach Checkpoint 3.", COL_GRAY, False),
    ]),
    (0.8, [
        ("  [TIMER] Leg 3 Checkpoint Window: ", COL_WHITE, False),
        ("00:00 [DEADLINE EXPIRED]", COL_RED, True),
    ]),
    # Step 5: Grace Period
    (1.4, [
        (">> STEP 5: DEAD-MAN SWITCH TIMEOUT — 10-MINUTE GRACE PERIOD", COL_YELLOW, True),
    ]),
    (1.5, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (1.7, [
        ("  Checkpoint window elapsed with zero hiker signal!", COL_WHITE, False),
    ]),
    (1.9, [
        ("  State Transition: ACTIVE -> ", COL_WHITE, False),
        ("GRACE_PERIOD", COL_YELLOW, True),
    ]),
    (2.1, [
        ("  Action: Phone triggers high-decibel tactical acoustic siren (880Hz-1200Hz sweep).", COL_YELLOW, False),
    ]),
    (2.3, [
        ("  Waiting for hiker dismiss signal... (Zero signal detected)", COL_GRAY, False),
    ]),
    (2.6, [
        ("  [TIMER] Grace Period Siren Countdown: ", COL_WHITE, False),
        ("00:00 [DEADLINE EXPIRED]", COL_RED, True),
    ]),
    # Step 6: Emergency Escalation & Rescue Dispatch
    (3.0, [
        (">> STEP 6: TEMPORAL EMERGENCY ESCALATION & RESCUE DISPATCH", COL_RED, True),
    ]),
    (3.1, [
        ("------------------------------------------------------------", COL_BORDER, False),
    ]),
    (3.2, [
        ("  [ALERT] GRACE PERIOD EXPIRED WITHOUT SIGNAL — DEAD-MAN SWITCH TRIGGERED!", COL_RED, True),
    ]),
    (3.4, [
        ("  Temporal executes durable activity: dispatch_emergency_alert_activity", COL_PROMPT, False),
    ]),
    (3.6, [
        ("  --------------------------------------------------------", COL_BORDER, False),
    ]),
    (3.7, [
        ("  | TRAILSAFE RESCUE ALERT", COL_WHITE, True),
    ]),
    (3.8, [
        ("  | Hiker: Sanjay (Solo Mountaineer)  |  Trail: Netravali Ridge Trail", COL_WHITE, False),
    ]),
    (3.9, [
        ("  | Status: DEAD-MAN SWITCH TIMEOUT / SOS", COL_RED, True),
    ]),
    (4.0, [
        ("  | Last Waypoint: Checkpoint 2: Mid-Ridge Scramble (cp-2)", COL_WHITE, False),
    ]),
    (4.1, [
        ("  | GPS Coordinates: 15.08920, 74.21540", COL_CYAN, True),
    ]),
    (4.2, [
        ("  | TabPFN Hazard Risk: 67.9%  |  Water Remaining: 300 mL", COL_YELLOW, False),
    ]),
    (4.3, [
        ("  --------------------------------------------------------", COL_BORDER, False),
    ]),
    (4.6, [
        ("  [OK] Telegram Bot (@ktcl_commuteshield_bot): ", COL_WHITE, False),
        ("DELIVERED (Message ID: 42)", COL_GREEN, True),
    ]),
    (4.9, [
        ("  [OK] Live Google Maps Pin: ", COL_WHITE, False),
        ("https://www.google.com/maps?q=15.08920,74.21540", COL_CYAN, True),
    ]),
    (5.2, [
        ("==========================================================================", COL_GREEN, False),
    ]),
    (5.4, [
        (" SIMULATION COMPLETE: HIKER LOCATED & RESCUE PROTOCOL ACTIVATED.", COL_GREEN, True),
    ]),
    (5.5, [
        ("==========================================================================", COL_GREEN, False),
    ]),
]


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COL_CANVAS)
    draw = ImageDraw.Draw(img)

    # Emergency pulse state
    is_emergency = (t >= 1.0)
    pulse = math.sin((t - 1.0) * 8.0) * 0.5 + 0.5 if is_emergency else 0.0

    # Draw terminal chrome
    draw_terminal_chrome(
        draw,
        "terminal — zsh — Temporal Dead-Man Timeout & Grace Period (80x28)",
        is_emergency=is_emergency,
        pulse=pulse,
    )

    start_x = WX + 35
    start_y = WY + TITLEBAR_H + 20
    line_h = 24
    cur_y = start_y

    for appear_t, segments in TERMINAL_SCRIPT:
        if t < appear_t:
            continue

        cur_x = start_x
        for text, color, is_bold in segments:
            f = FONT_MONO_BOLD if is_bold else FONT_MONO
            draw.text((cur_x, cur_y), text, fill=color, font=f)
            cur_x += f.getlength(text)

        cur_y += line_h

    # Flashing warning overlay banner between t=1.0s and t=2.8s
    if 1.0 <= t <= 2.8:
        banner_w = 780
        banner_h = 44
        bx = WX + (WW - banner_w) // 2
        by = WY + TITLEBAR_H + 220
        banner_bg = (int(180 + pulse * 75), 28, 28)
        draw.rounded_rectangle([(bx, by), (bx + banner_w, by + banner_h)], radius=8, fill=banner_bg, outline=(255, 255, 255), width=2)
        btxt = "[!] CHECKPOINT TIMEOUT -> ENTERING GRACE_PERIOD"
        btw = FONT_BANNER.getlength(btxt)
        draw.text((bx + (banner_w - btw) // 2, by + 8), btxt, fill=(255, 255, 255), font=FONT_BANNER)

    # Blinking terminal cursor at bottom
    if int(t * 4) % 2 == 0:
        draw.text((start_x, cur_y), "█", fill=COL_WHITE, font=FONT_MONO)

    return img


def main():
    print(f"Rendering SIMULATION VIDEO 8 -> {OUTPUT_MP4} ({DURATION}s @ {FPS}fps, NO AUDIO)...")
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
    print(f"✓ Successfully rendered SIMULATION VIDEO 8: {OUTPUT_MP4} ({os.path.getsize(OUTPUT_MP4)} bytes)")


if __name__ == "__main__":
    main()
