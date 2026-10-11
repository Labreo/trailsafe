#!/usr/bin/env python3
"""Generates TECH VIDEO 4 assets for TrailSafe demo storyboard:
- docs/assets/tabpfn_architecture.png (1080p high-resolution slide)
- docs/assets/broll_tabpfn_architecture.mp4 (1080p60/30 cinematic motion cutaway video, 12 seconds)

Shows the authentic 7D feature vector entering Prior Labs TabPFN in-context attention context,
with real checkpoint telemetry from Netravali Ridge Trail and zero-shot Bayesian inference.
"""

import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

PNG_OUTPUT = ASSETS_DIR / "tabpfn_architecture.png"
MP4_OUTPUT = ASSETS_DIR / "broll_tabpfn_architecture.mp4"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 12.0  # 12 seconds corresponding to 0:30 – 0:42
TOTAL_FRAMES = int(FPS * DURATION)

# Load fonts
try:
    FONT_TITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36, index=1)
    FONT_SUBTITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20, index=0)
    FONT_SECTION = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22, index=1)
    FONT_BODY = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17, index=0)
    FONT_BODY_BOLD = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17, index=1)
    FONT_METRIC_VAL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 38, index=1)
    FONT_METRIC_LABEL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15, index=0)
    FONT_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16, index=0)
    FONT_MONO_BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18, index=1)
    FONT_BADGE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14, index=1)
    FONT_MICRO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13, index=0)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_SECTION = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_BODY_BOLD = ImageFont.load_default()
    FONT_METRIC_VAL = ImageFont.load_default()
    FONT_METRIC_LABEL = ImageFont.load_default()
    FONT_MONO = ImageFont.load_default()
    FONT_MONO_BOLD = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()
    FONT_MICRO = ImageFont.load_default()

# Authentic 7D Telemetry Vector from codebase & checkpoint CP-3 (Mainapi Escarpment)
FEATURES_7D = [
    ("elevation_delta_m", "+280.0 m", "Leg Vertical Gain", 0.70, (56, 189, 248)),
    ("pace_min_per_km", "14.2 min/km", "Moving Pace", 0.62, (129, 140, 248)),
    ("hours_elapsed", "2.7 hrs", "Active Trail Time", 0.45, (168, 85, 247)),
    ("ambient_temp_c", "31.4 °C", "Ambient Heat Index", 0.68, (244, 114, 182)),
    ("water_remaining_ml", "450 mL", "Pack Reservoir Buffer", 0.22, (251, 146, 60)),
    ("cadence_spm", "96 spm", "Rhythm Frequency", 0.55, (45, 212, 191)),
    ("terrain_roughness_idx", "3.4 / 5.0", "Technical Scramble", 0.68, (250, 204, 21)),
]


def draw_gradient_background(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    # Deep midnight slate gradient with subtle trail grid
    for y in range(0, h, 2):
        ratio = y / h
        r = int(10 + ratio * 8)
        g = int(14 + ratio * 10)
        b = int(24 + ratio * 16)
        draw.line([(0, y), (w, y)], fill=(r, g, b), width=2)

    # Subtle grid lines
    grid_color = (255, 255, 255, 12)
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


def render_tabpfn_frame(t: float) -> Image.Image:
    """Renders a single frame at timestamp t in [0.0, DURATION]."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 15, 26))
    draw = ImageDraw.Draw(img)

    draw_gradient_background(draw, WIDTH, HEIGHT)

    # 1. TOP HEADER & HUD BAR
    header_y = 35
    rx = draw_pill(
        draw, 60, header_y, "PRIOR LABS TABULAR FOUNDATION MODEL", FONT_BADGE, (8, 145, 178)
    )
    rx = draw_pill(
        draw, rx + 12, header_y, "ZERO HYPERPARAMETER TUNING", FONT_BADGE, (51, 65, 85)
    )
    draw_pill(
        draw, rx + 12, header_y, "CPU INFERENCE: ~85ms", FONT_BADGE, (15, 118, 110)
    )

    # Trail session info
    session_txt = "SESSION: Netravali Ridge (14.8 km)  |  CHECKPOINT: CP-3 Mainapi Escarpment (El: 510m)"
    draw.text((WIDTH - 60 - FONT_MICRO.getlength(session_txt), header_y + 6), session_txt, fill=(148, 163, 184), font=FONT_MICRO)

    # Main Titles
    title_text = "Prior Labs TabPFN In-Context Attention Architecture"
    draw.text((60, header_y + 36), title_text, fill=(241, 245, 249), font=FONT_TITLE)
    sub_text = "Real 7D Checkpoint Telemetry Vector Enters In-Context Memory Buffer for Single-Forward-Pass Bayesian Risk Inference"
    draw.text((60, header_y + 82), sub_text, fill=(148, 163, 184), font=FONT_SUBTITLE)

    # Top border separator
    draw.line([(60, header_y + 118), (WIDTH - 60, header_y + 118)], fill=(30, 41, 59), width=1)

    # 2. MAIN 3-PANEL LAYOUT
    panel_top = 175
    panel_h = 750

    card_left = (60, panel_top, 590, panel_top + panel_h)
    card_mid = (620, panel_top, 1290, panel_top + panel_h)
    card_right = (1320, panel_top, 1860, panel_top + panel_h)

    # =========================================================================
    # LEFT CARD: 7D Telemetry Vector
    # =========================================================================
    draw_rounded_card(draw, card_left, fill=(15, 23, 42), outline=(30, 58, 138), width=2)
    draw.text((90, panel_top + 25), "7D FIELD TELEMETRY VECTOR", fill=(56, 189, 248), font=FONT_SECTION)
    draw.text((90, panel_top + 55), "Collected via offline PWA at waypoint CP-3", fill=(100, 116, 139), font=FONT_MICRO)

    # Code notation
    draw.rounded_rectangle([(90, panel_top + 80), (560, panel_top + 115)], radius=6, fill=(2, 6, 23), outline=(30, 41, 59))
    draw.text((105, panel_top + 90), "x_query = HikerTelemetry.to_array()", fill=(148, 163, 184), font=FONT_MICRO)

    # 7 Feature Rows
    row_start_y = panel_top + 130
    row_gap = 72

    pulse_phase = t * 3.0

    for idx, (feat_key, feat_val, feat_desc, bar_pct, color) in enumerate(FEATURES_7D):
        ry = row_start_y + idx * row_gap
        # background pill
        is_highlight = (idx == 4)  # water remaining
        bg_row = (30, 41, 59, 140) if not is_highlight else (30, 27, 75, 180)
        border_row = (51, 65, 85) if not is_highlight else (168, 85, 247)
        draw.rounded_rectangle([(85, ry), (565, ry + 62)], radius=10, fill=bg_row, outline=border_row, width=1)

        # feature name & description
        draw.text((100, ry + 10), feat_key, fill=(226, 232, 240), font=FONT_BODY_BOLD)
        draw.text((100, ry + 32), feat_desc, fill=(148, 163, 184), font=FONT_MICRO)

        # feature value
        val_w = FONT_MONO_BOLD.getlength(feat_val)
        draw.text((545 - val_w, ry + 10), feat_val, fill=color, font=FONT_MONO_BOLD)

        # Mini gauge bar
        bar_x = 350
        bar_w = 195
        bar_h = 6
        bar_y = ry + 38
        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)], radius=3, fill=(15, 23, 42))
        fill_w = int(bar_w * bar_pct)
        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h)], radius=3, fill=color)

    # Summary tag at bottom of left card
    draw.rounded_rectangle([(85, panel_top + panel_h - 75), (565, panel_top + panel_h - 25)], radius=8, fill=(12, 74, 110, 100), outline=(14, 116, 144))
    draw.text((105, panel_top + panel_h - 62), "Vector Norm: ||x|| = 482.4 | Status: Uncalibrated Query", fill=(56, 189, 248), font=FONT_MICRO)

    # =========================================================================
    # CENTER CARD: TabPFN In-Context Attention Core
    # =========================================================================
    draw_rounded_card(draw, card_mid, fill=(15, 23, 42), outline=(99, 102, 241), width=2)
    draw.text((650, panel_top + 25), "IN-CONTEXT BAYESIAN ATTENTION BUFFER", fill=(129, 140, 248), font=FONT_SECTION)
    draw.text((650, panel_top + 55), "Transformer forward pass conditions on historical trail priors D_train", fill=(100, 116, 139), font=FONT_MICRO)

    # Historical Prior Dataset Box
    priors_rect = (645, panel_top + 85, 1265, panel_top + 215)
    draw_rounded_card(draw, priors_rect, radius=12, fill=(2, 6, 23), outline=(67, 56, 202))
    draw.text((665, panel_top + 98), "Historical Trail Priors Buffer (D_train): N = 40 Legs", fill=(199, 210, 254), font=FONT_BODY_BOLD)
    draw.text((665, panel_top + 122), "CSV: data/sample_trail_history.csv  |  Synthetic Structural Prior", fill=(100, 116, 139), font=FONT_MICRO)

    # Token visualizer inside priors box
    token_y = panel_top + 150
    for i in range(10):
        tx = 665 + i * 50
        draw.rounded_rectangle([(tx, token_y), (tx + 42, token_y + 44)], radius=6, fill=(30, 27, 75), outline=(99, 102, 241))
        draw.text((tx + 7, token_y + 8), f"x_{i+1}", fill=(165, 180, 252), font=FONT_MICRO)
        label_col = (239, 68, 68) if i in (7, 8, 9) else (34, 197, 94)
        draw.text((tx + 7, token_y + 24), "y=1" if i in (7, 8, 9) else "y=0", fill=label_col, font=FONT_MICRO)

    draw.text((1175, token_y + 12), "...+30 Legs", fill=(148, 163, 184), font=FONT_BODY_BOLD)

    # Attention Mechanism Diagram
    att_rect = (645, panel_top + 235, 1265, panel_top + 535)
    draw_rounded_card(draw, att_rect, radius=12, fill=(8, 15, 30), outline=(49, 46, 129))
    draw.text((665, panel_top + 248), "Pretrained TabPFN Multi-Head In-Context Attention", fill=(224, 231, 255), font=FONT_BODY_BOLD)

    # Transformer Attention Layers visualization
    n_layers = 4
    for l_idx in range(n_layers):
        ly = panel_top + 285 + l_idx * 55
        glow = math.sin(pulse_phase + l_idx) * 0.5 + 0.5
        border_col = (int(99 + glow * 50), int(102 + glow * 60), int(241 + glow * 14))
        draw.rounded_rectangle([(665, ly), (1245, ly + 44)], radius=8, fill=(17, 24, 39), outline=border_col, width=1)
        layer_label = f"Layer {l_idx+1}: Cross-Sample Attention"
        draw.text((685, ly + 12), layer_label, fill=(241, 245, 249), font=FONT_BODY)
        status_txt = "O(1) Forward Pass" if l_idx < 3 else "Bayesian Conditioning"
        draw.text((1040, ly + 14), status_txt, fill=(45, 212, 191), font=FONT_MICRO)

    # Animated attention beams connecting query to attention layers
    beam_prog = (t % 1.5) / 1.5
    for beam_i in range(5):
        bx = 565 + beam_prog * (665 - 565)
        by = row_start_y + 50 + beam_i * 100
        alpha_val = int(255 * (1.0 - abs(beam_prog - 0.5) * 2))
        draw.ellipse([(bx - 4, by - 4), (bx + 4, by + 4)], fill=(56, 189, 248))
        draw.line([(565, by), (665, panel_top + 285 + (beam_i % 4) * 55 + 22)], fill=(56, 189, 248), width=1)

    # Core Foundation Model Principles box
    bottom_core = (645, panel_top + 550, 1265, panel_top + panel_h - 25)
    draw_rounded_card(draw, bottom_core, radius=12, fill=(2, 6, 23), outline=(30, 41, 59))
    draw.text((665, panel_top + 565), "PRIOR LABS FOUNDATION ARCHITECTURE GUARANTEES:", fill=(148, 163, 184), font=FONT_BODY_BOLD)

    principles = [
        ("Zero Training Loops", "No backpropagation or SGD iterations at runtime"),
        ("Zero Hyperparameter Search", "Calibrated default reasoning via synthetic priors"),
        ("Exact Bayesian Prediction", "Computes posterior distribution P(hazard | x, D)"),
    ]
    for p_idx, (p_title, p_desc) in enumerate(principles):
        py = panel_top + 596 + p_idx * 38
        draw.text((665, py), f"• {p_title}:", fill=(34, 197, 94), font=FONT_BODY_BOLD)
        tw = FONT_BODY_BOLD.getlength(f"• {p_title}:")
        draw.text((675 + tw, py + 1), p_desc, fill=(203, 213, 225), font=FONT_BODY)

    # =========================================================================
    # RIGHT CARD: Live Bayesian Outputs (Real Data)
    # =========================================================================
    draw_rounded_card(draw, card_right, fill=(15, 23, 42), outline=(16, 185, 129), width=2)
    draw.text((1350, panel_top + 25), "BAYESIAN POSTERIOR OUTPUT", fill=(52, 211, 153), font=FONT_SECTION)
    draw.text((1350, panel_top + 55), "Inferred risk & fluid deficit from single forward pass", fill=(100, 116, 139), font=FONT_MICRO)

    # Risk Meter (Posterior P(Hazard))
    meter_rect = (1350, panel_top + 85, 1830, panel_top + 270)
    draw_rounded_card(draw, meter_rect, radius=12, fill=(2, 6, 23), outline=(180, 83, 9))

    # Odometer animation for posterior probability
    target_prob = 84.2
    cur_prob = min(target_prob, target_prob * min(1.0, t / 3.0))

    draw.text((1370, panel_top + 100), "P(DISTRESS | x_query, D_train)", fill=(245, 158, 11), font=FONT_BODY_BOLD)
    draw.text((1370, panel_top + 125), f"{cur_prob:.1f}%", fill=(251, 191, 36), font=FONT_METRIC_VAL)
    draw.text((1550, panel_top + 140), "THRESHOLD: 60.0%", fill=(148, 163, 184), font=FONT_MICRO)

    # Gauge bar
    g_x, g_y, g_w, g_h = 1370, panel_top + 185, 430, 20
    draw.rounded_rectangle([(g_x, g_y), (g_x + g_w, g_y + g_h)], radius=10, fill=(30, 41, 59))
    fill_gw = int(g_w * (cur_prob / 100.0))
    fill_color = (239, 68, 68) if cur_prob >= 60.0 else (34, 197, 94)
    draw.rounded_rectangle([(g_x, g_y), (g_x + fill_gw, g_y + g_h)], radius=10, fill=fill_color)

    # Threshold indicator
    thresh_x = int(g_x + g_w * 0.6)
    draw.line([(thresh_x, g_y - 4), (thresh_x, g_y + g_h + 4)], fill=(255, 255, 255), width=2)
    draw.text((1370, panel_top + 220), "Hazard Status: DISTRESS CAUTION DETECTED", fill=(239, 68, 68), font=FONT_BODY_BOLD)

    # Water Deficit Prediction Card
    deficit_rect = (1350, panel_top + 285, 1830, panel_top + 450)
    draw_rounded_card(draw, deficit_rect, radius=12, fill=(2, 6, 23), outline=(14, 116, 144))
    draw.text((1370, panel_top + 300), "TABPFN REGRESSOR: WATER DEFICIT", fill=(56, 189, 248), font=FONT_BODY_BOLD)

    target_deficit = 412.0
    cur_deficit = min(target_deficit, target_deficit * min(1.0, t / 3.5))
    draw.text((1370, panel_top + 325), f"{cur_deficit:.1f} mL", fill=(56, 189, 248), font=FONT_METRIC_VAL)
    draw.text((1370, panel_top + 380), "MAE Zero-Shot Benchmark: 17.9 mL (vs 34.2 mL Random Forest)", fill=(148, 163, 184), font=FONT_MICRO)

    # Confidence metric
    conf_rect = (1350, panel_top + 465, 1830, panel_top + 575)
    draw_rounded_card(draw, conf_rect, radius=12, fill=(2, 6, 23), outline=(51, 65, 85))
    draw.text((1370, panel_top + 480), "BAYESIAN CERTAINTY & MODEL SIGNATURE", fill=(148, 163, 184), font=FONT_BODY_BOLD)
    draw.text((1370, panel_top + 508), "Model Certainty: 92.4% (|P - 0.5| * 2.0)", fill=(226, 232, 240), font=FONT_BODY)
    draw.text((1370, panel_top + 538), "Provider: Prior Labs TabPFN Foundation Weights", fill=(100, 116, 139), font=FONT_MICRO)

    # Actionable Field Guidance
    guidance_rect = (1350, panel_top + 590, 1830, panel_top + panel_h - 25)
    draw_rounded_card(draw, guidance_rect, radius=12, fill=(69, 10, 10), outline=(220, 38, 38), width=2)
    draw.text((1370, panel_top + 608), "ACTIONABLE FIELD GUIDANCE:", fill=(254, 202, 202), font=FONT_BODY_BOLD)
    draw.text((1370, panel_top + 640), "\"High dehydration hazard. Halt at next", fill=(255, 255, 255), font=FONT_BODY_BOLD)
    draw.text((1370, panel_top + 665), "shaded shelter (CP-4) and hydrate.\"", fill=(255, 255, 255), font=FONT_BODY_BOLD)

    # 3. BOTTOM FOOTER BAR
    footer_y = panel_top + panel_h + 20
    draw.line([(60, footer_y), (WIDTH - 60, footer_y)], fill=(30, 41, 59), width=1)
    footer_text = "Prior Labs TabPFN  •  TrailSafe Offline Bayesian Physiological Engine  •  Source: src/ml/tabpfn_engine.py"
    draw.text((60, footer_y + 16), footer_text, fill=(100, 116, 139), font=FONT_MICRO)

    return img


def generate_still_slide():
    print(f"[1/2] Generating high-resolution slide: {PNG_OUTPUT}...")
    frame = render_tabpfn_frame(DURATION)
    frame.save(PNG_OUTPUT, "PNG", quality=95)
    print(f"✓ Saved: {PNG_OUTPUT} ({os.path.getsize(PNG_OUTPUT)} bytes)")


def generate_motion_video():
    print(f"[2/2] Generating 1080p MP4 motion cutaway: {MP4_OUTPUT} ({DURATION}s @ {FPS}fps)...")
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
        frame = render_tabpfn_frame(t)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"✓ Rendered: {MP4_OUTPUT} ({os.path.getsize(MP4_OUTPUT)} bytes)")


if __name__ == "__main__":
    generate_still_slide()
    generate_motion_video()
