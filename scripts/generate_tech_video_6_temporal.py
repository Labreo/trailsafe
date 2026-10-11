#!/usr/bin/env python3
"""Generates TECH VIDEO 6 assets for TrailSafe demo storyboard:
- docs/assets/temporal_durable_execution.png (1080p high-resolution slide)
- docs/assets/broll_temporal_execution.mp4 (1080p motion video, 10 seconds)

Shows Temporal's durable execution engine and state persistence surviving reboots:
- Fragile (setTimeout / cron) vs Durable (Temporal state machine)
- Worker crash / reboot at t=32m and instant event history replay
- TrailSafetyWorkflow signals: check_in, extend_window, grace period (10m), emergency dispatch.
"""

import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

PNG_OUTPUT = ASSETS_DIR / "temporal_durable_execution.png"
MP4_OUTPUT = ASSETS_DIR / "broll_temporal_execution.mp4"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 10.0  # 10 seconds corresponding to 0:54 – 1:04
TOTAL_FRAMES = int(FPS * DURATION)

# Load fonts
try:
    FONT_TITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36, index=1)
    FONT_SUBTITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20, index=0)
    FONT_SECTION = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22, index=1)
    FONT_BODY = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17, index=0)
    FONT_BODY_BOLD = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17, index=1)
    FONT_BIG_VAL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36, index=1)
    FONT_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15, index=0)
    FONT_MONO_BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 17, index=1)
    FONT_BADGE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14, index=1)
    FONT_MICRO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13, index=0)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_SECTION = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_BODY_BOLD = ImageFont.load_default()
    FONT_BIG_VAL = ImageFont.load_default()
    FONT_MONO = ImageFont.load_default()
    FONT_MONO_BOLD = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()
    FONT_MICRO = ImageFont.load_default()


def draw_gradient_background(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    for y in range(0, h, 2):
        ratio = y / h
        r = int(10 + ratio * 8)
        g = int(14 + ratio * 10)
        b = int(24 + ratio * 16)
        draw.line([(0, y), (w, y)], fill=(r, g, b), width=2)

    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(20, 30, 48), width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(20, 30, 48), width=1)


def draw_rounded_card(
    draw: ImageDraw.ImageDraw,
    rect: tuple,
    radius: int = 16,
    fill=(17, 24, 39, 230),
    outline=(55, 65, 81),
    width: int = 1,
) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)


def draw_pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font,
    bg_color,
    text_color=(255, 255, 255),
    padding=(12, 6),
) -> int:
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw, ph = padding
    rect = (x, y, x + tw + pw * 2, y + th + ph * 2)
    draw.rounded_rectangle(rect, radius=int((th + ph * 2) / 2), fill=bg_color)
    draw.text((x + pw, y + ph - 1), text, fill=text_color, font=font)
    return x + tw + pw * 2


def render_temporal_frame(t: float) -> Image.Image:
    """Renders a single frame at timestamp t in [0.0, DURATION]."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 15, 26))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, WIDTH, HEIGHT)

    # 1. TOP HEADER & HUD
    header_y = 35
    rx = draw_pill(draw, 60, header_y, "TEMPORAL DURABLE EXECUTION", FONT_BADGE, (139, 92, 246))
    rx = draw_pill(draw, rx + 12, header_y, "TASK QUEUE: trailsafe-task-queue", FONT_BADGE, (51, 65, 85))
    draw_pill(draw, rx + 12, header_y, "WORKFLOW: TrailSafetyWorkflow", FONT_BADGE, (15, 118, 110))

    src_txt = "SRC: src/temporal/workflows.py  |  SDK: temporalio v1.34"
    draw.text((WIDTH - 60 - FONT_MICRO.getlength(src_txt), header_y + 6), src_txt, fill=(148, 163, 184), font=FONT_MICRO)

    title_text = "Temporal Durable Execution: Surviving Phone Reboots"
    draw.text((60, header_y + 36), title_text, fill=(241, 245, 249), font=FONT_TITLE)
    sub_text = "Why Basic Sleep Timers / Cron Jobs Fail Outdoors vs. How Temporal Replays Event History With Zero State Loss"
    draw.text((60, header_y + 82), sub_text, fill=(148, 163, 184), font=FONT_SUBTITLE)

    draw.line([(60, header_y + 118), (WIDTH - 60, header_y + 118)], fill=(30, 41, 59), width=1)

    panel_top = 175

    # 2. TOP HALF: COMPARISON (Fragile vs Durable)
    comp_h = 360
    card_w = 880

    # Timing variables for motion
    # t < 2.5: Normal countdown
    # 2.5 <= t < 5.0: Crash simulation (t=32m)
    # 5.0 <= t < 7.5: Event History Replay
    # t >= 7.5: Resumed countdown & grace period escalation
    is_crashed = (2.5 <= t < 5.0)
    is_replaying = (5.0 <= t < 7.5)
    is_resumed = (t >= 7.5)

    pulse_glow = math.sin(t * 3.5) * 0.5 + 0.5

    # =========================================================================
    # LEFT CARD: Fragile Architecture
    # =========================================================================
    card_left = (60, panel_top, 60 + card_w, panel_top + comp_h)
    draw_rounded_card(draw, card_left, fill=(24, 15, 15), outline=(220, 38, 38), width=2)

    draw.text((85, panel_top + 20), "FRAGILE: Standard setTimeout / Cron / Device Sleep", fill=(248, 113, 113), font=FONT_SECTION)
    draw.text((85, panel_top + 48), "Volatile in-memory timer (standard mobile outdoor apps)", fill=(148, 163, 184), font=FONT_MICRO)

    # Status / Timer Box
    timer_box_left = (85, panel_top + 75, 60 + card_w - 25, panel_top + 165)
    left_timer_bg = (69, 10, 10) if is_crashed or is_replaying or is_resumed else (40, 15, 15)
    draw_rounded_card(draw, timer_box_left, radius=10, fill=left_timer_bg, outline=(185, 28, 28))

    if t < 2.5:
        draw.text((105, panel_top + 88), "TIMER STATUS: RUNNING (In-Memory setTimeout)", fill=(254, 202, 202), font=FONT_BODY_BOLD)
        draw.text((105, panel_top + 115), "32:15 Remaining (45:00 window)", fill=(248, 113, 113), font=FONT_BIG_VAL)
    else:
        draw.text((105, panel_top + 88), "TIMER STATUS: CRASHED & TERMINATED", fill=(255, 100, 100), font=FONT_BODY_BOLD)
        draw.text((105, panel_top + 115), "00:00 [MEMORY ERASED]", fill=(239, 68, 68), font=FONT_BIG_VAL)
        draw_pill(draw, 580, panel_top + 118, "TIMER LOST", FONT_BADGE, (185, 28, 28))

    # Consequence bullet points
    draw.text((85, panel_top + 180), "FAILURE MODE WHEN HIKING SOLO IN WESTERN GHATS:", fill=(254, 202, 202), font=FONT_BODY_BOLD)
    fragile_points = [
        ("OS Memory Kill:", "iOS / Android kills background web tabs after 3 minutes to save battery."),
        ("Phone Reboot:", "If phone dies or reboots in cold rain, the in-memory timer is permanently erased."),
        ("Fatal Consequence:", "Hiker is injured at CP-3; countdown never fires; NO RESCUE SIGNAL SENT!"),
    ]
    for idx, (f_head, f_desc) in enumerate(fragile_points):
        fy = panel_top + 210 + idx * 30
        draw.text((85, fy), f"• {f_head}", fill=(239, 68, 68), font=FONT_BODY_BOLD)
        thw = FONT_BODY_BOLD.getlength(f"• {f_head}")
        draw.text((95 + thw, fy), f_desc, fill=(203, 213, 225), font=FONT_BODY)

    draw.rounded_rectangle([(85, panel_top + comp_h - 45), (60 + card_w - 25, panel_top + comp_h - 15)], radius=6, fill=(45, 10, 10))
    draw.text((100, panel_top + comp_h - 35), "RESULT: Unreliable safety net. Solo hiker remains stranded without alert.", fill=(248, 113, 113), font=FONT_MICRO)

    # =========================================================================
    # RIGHT CARD: Temporal Durable Architecture
    # =========================================================================
    card_right = (WIDTH - 60 - card_w, panel_top, WIDTH - 60, panel_top + comp_h)
    draw_rounded_card(draw, card_right, fill=(8, 30, 45), outline=(16, 185, 129), width=2)

    draw.text((WIDTH - 60 - card_w + 25, panel_top + 20), "DURABLE: Temporal Workflow Orchestration", fill=(52, 211, 153), font=FONT_SECTION)
    draw.text((WIDTH - 60 - card_w + 25, panel_top + 48), "Deterministic state machine backed by persistent event history", fill=(148, 163, 184), font=FONT_MICRO)

    # Status / Timer Box
    timer_box_right = (WIDTH - 60 - card_w + 25, panel_top + 75, WIDTH - 60 - 25, panel_top + 165)
    draw_rounded_card(draw, timer_box_right, radius=10, fill=(4, 47, 46), outline=(13, 148, 136))

    if t < 2.5:
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 88), "WORKFLOW STATE: ACTIVE_COUNTDOWN", fill=(153, 246, 228), font=FONT_BODY_BOLD)
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 115), "32:15 Remaining", fill=(45, 212, 191), font=FONT_BIG_VAL)
        draw_pill(draw, WIDTH - 60 - card_w + 500, panel_top + 118, "DURABLE TIMER", FONT_BADGE, (13, 148, 136))
    elif is_crashed:
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 88), "WORKER SHUTDOWN DETECTED (t=32m reboot)", fill=(251, 191, 36), font=FONT_BODY_BOLD)
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 115), "PERSISTED IN CLUSTER", fill=(245, 158, 11), font=FONT_BIG_VAL)
        draw_pill(draw, WIDTH - 60 - card_w + 500, panel_top + 118, "STATE PRESERVED", FONT_BADGE, (180, 83, 9))
    elif is_replaying:
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 88), "REPLAYING EVENT HISTORY IN-MEMORY...", fill=(125, 211, 252), font=FONT_BODY_BOLD)
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 115), "REHYDRATED IN 12ms", fill=(56, 189, 248), font=FONT_BIG_VAL)
        draw_pill(draw, WIDTH - 60 - card_w + 500, panel_top + 118, "ZERO DATA LOSS", FONT_BADGE, (8, 145, 178))
    else:
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 88), "WORKFLOW RESUMED AT EXACT STATE", fill=(110, 231, 183), font=FONT_BODY_BOLD)
        draw.text((WIDTH - 60 - card_w + 45, panel_top + 115), "32:10 Remaining", fill=(52, 211, 153), font=FONT_BIG_VAL)
        draw_pill(draw, WIDTH - 60 - card_w + 500, panel_top + 118, "ACTIVE PROTECTED", FONT_BADGE, (5, 150, 105))

    # Durable advantages
    draw.text((WIDTH - 60 - card_w + 25, panel_top + 180), "HOW TEMPORAL SURVIVES MOUNTAIN REBOOTS:", fill=(167, 243, 208), font=FONT_BODY_BOLD)
    durable_points = [
        ("Append-Only Event History:", "Workflow commands & signals are recorded durably in SQLite / cluster."),
        ("Instant Event Replay:", "When worker reboots, it replays past events and recovers state in < 15ms."),
        ("Guaranteed Escalation:", "If countdown expires with zero signal, safety grace period fires automatically!"),
    ]
    for idx, (d_head, d_desc) in enumerate(durable_points):
        dy = panel_top + 210 + idx * 30
        draw.text((WIDTH - 60 - card_w + 25, dy), f"• {d_head}", fill=(52, 211, 153), font=FONT_BODY_BOLD)
        thw = FONT_BODY_BOLD.getlength(f"• {d_head}")
        draw.text((WIDTH - 60 - card_w + 35 + thw, dy), d_desc, fill=(203, 213, 225), font=FONT_BODY)

    draw.rounded_rectangle([(WIDTH - 60 - card_w + 25, panel_top + comp_h - 45), (WIDTH - 60 - 25, panel_top + comp_h - 15)], radius=6, fill=(6, 78, 59))
    draw.text((WIDTH - 60 - card_w + 40, panel_top + comp_h - 35), "RESULT: 100% durable protection. Checkpoints, signals, and deadlines survive all restarts.", fill=(167, 243, 208), font=FONT_MICRO)

    # =========================================================================
    # 3. BOTTOM HALF: END-TO-END WORKFLOW PIPELINE ARCHITECTURE (4 Stages)
    # =========================================================================
    pipe_top = panel_top + comp_h + 20
    pipe_h = 360
    card_pipe = (60, pipe_top, WIDTH - 60, pipe_top + pipe_h)
    draw_rounded_card(draw, card_pipe, fill=(15, 23, 42), outline=(99, 102, 241), width=2)

    draw.text((85, pipe_top + 20), "END-TO-END TEMPORAL SAFETY WORKFLOW ESCALATION PIPELINE", fill=(129, 140, 248), font=FONT_SECTION)
    draw.text((85, pipe_top + 48), "State Machine, Signal Channels, In-Context TabPFN Inference & Multi-Channel Dispatch", fill=(100, 116, 139), font=FONT_MICRO)

    stages = [
        (
            "1. Client Signals",
            "Screen-Zero PWA",
            [
                "check_in(telemetry)",
                "extend_window(mins)",
                "emergency_sos(reason)",
            ],
            (56, 189, 248),
        ),
        (
            "2. Temporal Cluster",
            "Event History Log",
            [
                "WorkflowStarted",
                "TimerStarted (45m)",
                "evaluate_tabpfn_risk",
            ],
            (129, 140, 248),
        ),
        (
            "3. Safety Countdown",
            "Dead-Man's Switch",
            [
                "45-Min Checkpoint Window",
                "Timeout -> GRACE_PERIOD",
                "10-Min Acoustic Siren",
            ],
            (251, 191, 36),
        ),
        (
            "4. Rescue Dispatch",
            "Multi-Channel Alert",
            [
                "dispatch_emergency_alert",
                "Telegram: @ktcl_bot",
                "GPS: 15.08920, 74.21540",
            ],
            (239, 68, 68),
        ),
    ]

    stage_w = 405
    stage_gap = 25
    stage_start_x = 85
    stage_box_y = pipe_top + 75
    stage_box_h = 245

    for s_idx, (s_title, s_sub, s_items, s_col) in enumerate(stages):
        sx = stage_start_x + s_idx * (stage_w + stage_gap)
        s_rect = (sx, stage_box_y, sx + stage_w, stage_box_y + stage_box_h)
        draw_rounded_card(draw, s_rect, radius=12, fill=(2, 6, 23), outline=(51, 65, 85))

        # Title pill
        draw_rounded_rectangle = draw.rounded_rectangle([(sx + 15, stage_box_y + 15), (sx + stage_w - 15, stage_box_y + 48)], radius=6, fill=(30, 41, 59))
        draw.text((sx + 25, stage_box_y + 22), s_title, fill=s_col, font=FONT_BODY_BOLD)

        draw.text((sx + 20, stage_box_y + 60), s_sub, fill=(148, 163, 184), font=FONT_MICRO)
        draw.line([(sx + 20, stage_box_y + 80), (sx + stage_w - 20, stage_box_y + 80)], fill=(30, 41, 59), width=1)

        # Items
        for it_idx, it_text in enumerate(s_items):
            iy = stage_box_y + 95 + it_idx * 42
            draw.rounded_rectangle([(sx + 15, iy), (sx + stage_w - 15, iy + 34)], radius=6, fill=(15, 23, 42), outline=(51, 65, 85))
            draw.text((sx + 25, iy + 8), f"> {it_text}", fill=(241, 245, 249), font=FONT_MONO)

        # Connecting arrow to next stage
        if s_idx < len(stages) - 1:
            ax = sx + stage_w + 6
            ay = stage_box_y + int(stage_box_h / 2)
            draw.line([(ax, ay), (ax + 12, ay)], fill=(99, 102, 241), width=2)
            draw.polygon([(ax + 12, ay - 4), (ax + 18, ay), (ax + 12, ay + 4)], fill=(99, 102, 241))

    # 4. FOOTER
    footer_y = pipe_top + pipe_h + 20
    draw.line([(60, footer_y), (WIDTH - 60, footer_y)], fill=(30, 41, 59), width=1)
    footer_text = "Temporal Durable Execution  •  TrailSafe Fault-Tolerant Outdoor Safety  •  Source: src/temporal/workflows.py"
    draw.text((60, footer_y + 16), footer_text, fill=(100, 116, 139), font=FONT_MICRO)

    return img


def generate_still_slide():
    print(f"[1/2] Generating Temporal slide: {PNG_OUTPUT}...")
    canvas = render_temporal_frame(DURATION)
    canvas.save(PNG_OUTPUT, "PNG", quality=95)
    print(f"✓ Saved: {PNG_OUTPUT} ({os.path.getsize(PNG_OUTPUT)} bytes)")


def generate_motion_video():
    print(f"[2/2] Generating 1080p Temporal execution motion MP4: {MP4_OUTPUT} ({DURATION}s @ {FPS}fps)...")
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
        str(MP4_OUTPUT)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(TOTAL_FRAMES):
        t = i / FPS
        frame = render_temporal_frame(t)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"✓ Rendered: {MP4_OUTPUT} ({os.path.getsize(MP4_OUTPUT)} bytes)")


if __name__ == "__main__":
    generate_still_slide()
    generate_motion_video()
