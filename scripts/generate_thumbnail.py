#!/usr/bin/env python3
"""Generates a pixel-perfect, high-converting 16:9 YouTube / Video Demo thumbnail for TrailSafe.
Resolution: 1920x1080 (Full HD, 16:9 standard).
Saves to: docs/assets/youtube_thumbnail.png

Features:
- Real official SVG logos:
  * Prior Labs official logo (from docs/assets/priorlabs_clean_logo.png)
  * Temporal official logo (from docs/assets/temporal_clean_logo.png)
  * TrailSafe shield vector logo (from docs/assets/trailsafe_logo.png)
- Perfect geometric centering and dynamic text bounding box calculations.
- Zero text escaping boundaries or running off edges.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "docs" / "assets"
OUTPUT_PNG = ASSETS_DIR / "youtube_thumbnail.png"
MOUNTAIN_FRAMES_DIR = Path("/tmp/ghats_frames")

WIDTH, HEIGHT = 1920, 1080

def ensure_clean_logos():
    """Converts SVGs/PNGs into crisp transparent logos with exact brand colors."""
    # 1. Temporal Logo
    temporal_clean_path = ASSETS_DIR / "temporal_clean_logo.png"
    if not temporal_clean_path.exists():
        im = Image.open(ASSETS_DIR / "temporal_logo.png").convert("RGB")
        gray = ImageOps.grayscale(im)
        arr = np.array(gray)
        alpha = np.clip((255 - arr) * 2.0, 0, 255).astype(np.uint8)
        color_arr = np.zeros((im.size[1], im.size[0], 4), dtype=np.uint8)
        color_arr[:, :, 0] = 56   # Cyan R
        color_arr[:, :, 1] = 189  # Cyan G
        color_arr[:, :, 2] = 248  # Cyan B
        color_arr[:, :, 3] = alpha
        res = Image.fromarray(color_arr, "RGBA")
        bbox = res.getbbox()
        res.crop(bbox).save(temporal_clean_path)

    # 2. Prior Labs Logo (White with glowing cyan icon)
    prior_clean_path = ASSETS_DIR / "priorlabs_clean_logo.png"
    if not prior_clean_path.exists():
        im = Image.open(ASSETS_DIR / "priorlabs_logo.png").convert("RGB")
        gray = ImageOps.grayscale(im)
        arr = np.array(gray)
        alpha = np.clip((255 - arr) * 2.2, 0, 255).astype(np.uint8)
        color_arr = np.zeros((im.size[1], im.size[0], 4), dtype=np.uint8)
        color_arr[:, :, 0] = 255  # White
        color_arr[:, :, 1] = 255
        color_arr[:, :, 2] = 255
        color_arr[:, :, 3] = alpha
        res = Image.fromarray(color_arr, "RGBA")
        bbox = res.getbbox()
        res.crop(bbox).save(prior_clean_path)

def get_scenery():
    frame_file = MOUNTAIN_FRAMES_DIR / "frame_0060.jpg"
    if frame_file.exists():
        base = Image.open(frame_file).convert("RGB")
        base = base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    else:
        base = Image.new("RGB", (WIDTH, HEIGHT), (12, 18, 24))
        draw = ImageDraw.Draw(base)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(10 + 15 * ratio)
            g = int(22 + 25 * ratio)
            b = int(25 + 30 * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return base

def draw_thumbnail():
    ensure_clean_logos()
    base = get_scenery()

    # Cinematic gradient overlay
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Left-weighted dark gradient to guarantee typography legibility
    for x in range(WIDTH):
        # Heavy on left (245 alpha), gradual drop off on right (155 alpha)
        alpha = int(245 - 90 * (x / WIDTH))
        odraw.line([(x, 0), (x, HEIGHT)], fill=(6, 10, 16, alpha))

    # Top & bottom subtle letterbox
    for y in range(120):
        alpha = int(180 * (1.0 - y / 120.0))
        odraw.line([(0, y), (WIDTH, y)], fill=(2, 5, 8, alpha))
        odraw.line([(0, HEIGHT - 1 - y), (WIDTH, HEIGHT - 1 - y)], fill=(2, 5, 8, alpha))

    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base, "RGBA")

    # Load system typography
    try:
        font_kicker = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 19, index=0)
        font_hero_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 92)
        font_hero_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 40)
        font_hook = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
        font_card_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
        font_card_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
        font_badge = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16, index=0)
        font_footer = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 19)
    except Exception:
        font_kicker = ImageFont.load_default()
        font_hero_title = ImageFont.load_default()
        font_hero_sub = ImageFont.load_default()
        font_hook = ImageFont.load_default()
        font_card_title = ImageFont.load_default()
        font_card_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Geometry Layout
    MARGIN_LEFT = 90
    CONTENT_WIDTH_LEFT = 920

    # 1. Kicker Badge (Top left)
    kicker_y = 65
    kicker_text = "HACKTOBERFEST 2026 // OPEN-SOURCE AI CHALLENGE"
    tb_k = draw.textbbox((0, 0), kicker_text, font=font_kicker)
    kw = tb_k[2] - tb_k[0]
    draw.rounded_rectangle(
        [(MARGIN_LEFT, kicker_y), (MARGIN_LEFT + kw + 32, kicker_y + 42)],
        radius=8,
        fill=(15, 23, 42, 240),
        outline=(56, 189, 248, 200),
        width=1
    )
    draw.text((MARGIN_LEFT + 16, kicker_y + 11), kicker_text, fill=(56, 189, 248, 255), font=font_kicker)

    # 2. Main Title: TRAILSAFE (Bold, white, sharp shadow)
    title_y = 125
    title_text = "TRAILSAFE"
    for dx, dy in [(3, 3), (-3, 3), (3, -3), (-3, -3), (0, 4)]:
        draw.text((MARGIN_LEFT + dx, title_y + dy), title_text, fill=(0, 0, 0, 220), font=font_hero_title)
    draw.text((MARGIN_LEFT, title_y), title_text, fill=(255, 255, 255), font=font_hero_title)

    # 3. Subtitle: TOUCH GRASS SAFELY (Bright Emerald)
    sub_y = 230
    sub_text = "TOUCH GRASS SAFELY"
    draw.text((MARGIN_LEFT, sub_y), sub_text, fill=(52, 211, 153), font=font_hero_sub)

    # 4. Hook Line: Zero Cell Coverage? You're Still Protected.
    hook_y = 295
    hook_text = "Zero Cell Coverage? You're Still Protected."
    draw.text((MARGIN_LEFT, hook_y), hook_text, fill=(226, 232, 240), font=font_hook)

    # 5. Three High-Tech Cards with Real Logos
    # Card 1: Prior Labs TabPFN
    # Card 2: Temporal Durable Workflows
    # Card 3: 100% Offline Edge Resilience
    cards_start_y = 360
    card_w = CONTENT_WIDTH_LEFT
    card_h = 104
    card_gap = 20

    # Load transparent logos
    prior_logo = Image.open(ASSETS_DIR / "priorlabs_clean_logo.png").convert("RGBA")
    temporal_logo = Image.open(ASSETS_DIR / "temporal_clean_logo.png").convert("RGBA")

    # Card Specifications
    cards_data = [
        {
            "brand": "priorlabs",
            "title": "Prior Labs TabPFN In-Context AI",
            "subtitle": "17.9 mL MAE Fluid Deficit Forecast · Outperforms RF by 2x",
            "col_accent": (16, 185, 129), # Emerald
            "badge": "FOUNDATION MODEL"
        },
        {
            "brand": "temporal",
            "title": "Temporal Durable Execution",
            "subtitle": "Durable Dead Man's Switch survives battery death & reboot",
            "col_accent": (56, 189, 248), # Cyan
            "badge": "WORKFLOW ENGINE"
        },
        {
            "brand": "offline",
            "title": "100% Offline Edge Resilience",
            "subtitle": "Zero cloud reliance · Local GPS, PWA cache & telemetry ledger",
            "col_accent": (245, 158, 11), # Amber
            "badge": "SCREEN-ZERO"
        }
    ]

    for idx, c in enumerate(cards_data):
        cy = cards_start_y + idx * (card_h + card_gap)
        col = c["col_accent"]

        # Card container
        draw.rounded_rectangle(
            [(MARGIN_LEFT, cy), (MARGIN_LEFT + card_w, cy + card_h)],
            radius=14,
            fill=(13, 20, 32, 220),
            outline=(col[0], col[1], col[2], 160),
            width=2
        )
        # Left accent strip
        draw.rounded_rectangle(
            [(MARGIN_LEFT + 4, cy + 4), (MARGIN_LEFT + 14, cy + card_h - 4)],
            radius=5,
            fill=(col[0], col[1], col[2], 255)
        )

        # Brand Logo Badge Box
        LOGO_BOX_X = MARGIN_LEFT + 28
        LOGO_BOX_Y = cy + 16
        LOGO_BOX_W = 140
        LOGO_BOX_H = 72

        draw.rounded_rectangle(
            [(LOGO_BOX_X, LOGO_BOX_Y), (LOGO_BOX_X + LOGO_BOX_W, LOGO_BOX_Y + LOGO_BOX_H)],
            radius=10,
            fill=(18, 27, 44, 230),
            outline=(col[0], col[1], col[2], 90),
            width=1
        )

        # Render Logo inside box
        if c["brand"] == "priorlabs":
            # Prior Labs wide logo
            # Target size: width 118, preserve aspect ratio
            pw = 118
            ph = int(prior_logo.height * (pw / prior_logo.width))
            p_resized = prior_logo.resize((pw, ph), Image.Resampling.LANCZOS)
            px = LOGO_BOX_X + (LOGO_BOX_W - pw) // 2
            py = LOGO_BOX_Y + (LOGO_BOX_H - ph) // 2
            base.paste(p_resized, (px, py), p_resized)

        elif c["brand"] == "temporal":
            # Temporal icon (square) + text
            # Icon size: 48x48
            tw = 48
            th = 48
            t_resized = temporal_logo.resize((tw, th), Image.Resampling.LANCZOS)
            tx = LOGO_BOX_X + (LOGO_BOX_W - tw) // 2
            ty = LOGO_BOX_Y + (LOGO_BOX_H - th) // 2
            base.paste(t_resized, (tx, ty), t_resized)

        elif c["brand"] == "offline":
            # Draw crisp custom Offline Signal Vector Badge
            off_cx = LOGO_BOX_X + LOGO_BOX_W // 2
            off_cy = LOGO_BOX_Y + LOGO_BOX_H // 2
            od = ImageDraw.Draw(base, "RGBA")
            # Shield contour
            od.polygon([
                (off_cx, off_cy - 22),
                (off_cx + 20, off_cy - 12),
                (off_cx + 14, off_cy + 14),
                (off_cx, off_cy + 22),
                (off_cx - 14, off_cy + 14),
                (off_cx - 20, off_cy - 12),
            ], fill=(245, 158, 11, 40), outline=(245, 158, 11, 220))
            # Text '0G' or 'OFF'
            tb_off = od.textbbox((0, 0), "OFFLINE", font=font_badge)
            od.text((off_cx - (tb_off[2] - tb_off[0]) // 2, off_cy - 8), "OFFLINE", fill=(255, 255, 255), font=font_badge)

        # Text Section inside card
        TEXT_X = LOGO_BOX_X + LOGO_BOX_W + 24
        draw.text((TEXT_X, cy + 22), c["title"], fill=(255, 255, 255), font=font_card_title)
        draw.text((TEXT_X, cy + 58), c["subtitle"], fill=(180, 195, 215), font=font_card_sub)

        # Right Tag in card
        badge_str = c["badge"]
        tb_b = draw.textbbox((0, 0), badge_str, font=font_badge)
        bw = tb_b[2] - tb_b[0]
        bh = tb_b[3] - tb_b[1]
        badge_x = MARGIN_LEFT + card_w - bw - 38
        badge_y = cy + 22
        draw.rounded_rectangle(
            [(badge_x - 12, badge_y - 5), (badge_x + bw + 12, badge_y + bh + 7)],
            radius=6,
            fill=(col[0], col[1], col[2], 35),
            outline=(col[0], col[1], col[2], 210),
            width=1
        )
        draw.text((badge_x, badge_y), badge_str, fill=(col[0], col[1], col[2]), font=font_badge)

    # 6. Bottom Highlight Bar under cards
    meta_y = cards_start_y + 3 * (card_h + card_gap) + 10
    draw.rounded_rectangle(
        [(MARGIN_LEFT, meta_y), (MARGIN_LEFT + card_w, meta_y + 60)],
        radius=10,
        fill=(10, 16, 28, 220),
        outline=(56, 189, 248, 100),
        width=1
    )
    meta_text = "EMPIRICAL BENCHMARK: 17.9 mL FLUID DEFICIT MAE  ·  ZERO-SHOT BAYESIAN POSTERIOR"
    tb_m = draw.textbbox((0, 0), meta_text, font=font_badge)
    mw = tb_m[2] - tb_m[0]
    draw.text((MARGIN_LEFT + (card_w - mw) // 2, meta_y + 20), meta_text, fill=(56, 189, 248), font=font_badge)

    # -------------------------------------------------------------------------
    # RIGHT COLUMN: Centered Glassmorphic HUD with TrailSafe Shield Logo
    # -------------------------------------------------------------------------
    RIGHT_COL_X = MARGIN_LEFT + CONTENT_WIDTH_LEFT + 60
    RIGHT_COL_W = WIDTH - RIGHT_COL_X - 90  # Exactly 760px wide
    HUD_CX = RIGHT_COL_X + RIGHT_COL_W // 2
    HUD_CY = HEIGHT // 2 - 20
    HUD_W = min(RIGHT_COL_W, 680)
    HUD_H = 680

    # Draw Glassmorphic HUD Card
    hud_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(hud_overlay)

    hdraw.rounded_rectangle(
        [(HUD_CX - HUD_W // 2, HUD_CY - HUD_H // 2), (HUD_CX + HUD_W // 2, HUD_CY + HUD_H // 2)],
        radius=24,
        fill=(11, 18, 30, 215),
        outline=(52, 211, 153, 160),
        width=2
    )

    # Subtle grid accent inside HUD
    for gy in range(HUD_CY - HUD_H // 2 + 60, HUD_CY + HUD_H // 2 - 60, 60):
        hdraw.line([(HUD_CX - HUD_W // 2 + 30, gy), (HUD_CX + HUD_W // 2 - 30, gy)], fill=(52, 211, 153, 20), width=1)
    for gx in range(HUD_CX - HUD_W // 2 + 60, HUD_CX + HUD_W // 2 - 60, 60):
        hdraw.line([(gx, HUD_CY - HUD_H // 2 + 30), (gx, HUD_CY + HUD_H // 2 - 30)], fill=(52, 211, 153, 20), width=1)

    base = Image.alpha_composite(base.convert("RGBA"), hud_overlay).convert("RGB")

    # Paste TrailSafe Shield Logo
    trailsafe_logo = Image.open(ASSETS_DIR / "trailsafe_logo.png").convert("RGBA")
    logo_sz = 430
    logo_scaled = trailsafe_logo.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    base.paste(logo_scaled, (HUD_CX - logo_sz // 2, HUD_CY - logo_sz // 2 - 25), logo_scaled)

    # Telemetry Badges inside HUD
    draw_hud = ImageDraw.Draw(base, "RGBA")

    # Top Tag
    top_tag = "WESTERN GHATS  //  15.0892°N, 74.2154°E"
    tb_tt = draw_hud.textbbox((0, 0), top_tag, font=font_badge)
    tt_w = tb_tt[2] - tb_tt[0]
    draw_hud.text((HUD_CX - tt_w // 2, HUD_CY - HUD_H // 2 + 25), top_tag, fill=(148, 163, 184), font=font_badge)

    # Bottom SAR Protocol Badge
    sar_str = "AUTONOMOUS SAR ESCALATION PROTOCOL"
    tb_sar = draw_hud.textbbox((0, 0), sar_str, font=font_kicker)
    sar_w = tb_sar[2] - tb_sar[0]
    sar_box_y = HUD_CY + HUD_H // 2 - 68

    draw_hud.rounded_rectangle(
        [(HUD_CX - sar_w // 2 - 20, sar_box_y), (HUD_CX + sar_w // 2 + 20, sar_box_y + 44)],
        radius=8,
        fill=(52, 211, 153, 30),
        outline=(52, 211, 153, 220),
        width=1
    )
    draw_hud.text((HUD_CX - sar_w // 2, sar_box_y + 11), sar_str, fill=(52, 211, 153), font=font_kicker)

    # -------------------------------------------------------------------------
    # 7. Global Bottom Footer Bar (Properly Padded, Never Escaping Border)
    # -------------------------------------------------------------------------
    FOOTER_H = 65
    draw_footer = ImageDraw.Draw(base, "RGBA")
    draw_footer.rectangle([(0, HEIGHT - FOOTER_H), (WIDTH, HEIGHT)], fill=(4, 7, 12, 250))
    draw_footer.line([(0, HEIGHT - FOOTER_H), (WIDTH, HEIGHT - FOOTER_H)], fill=(56, 189, 248, 90), width=1)

    # Left footer item
    footer_left = "GITHUB: github.com/Labreo/trailsafe  ·  MIT LICENSE"
    draw_footer.text((MARGIN_LEFT, HEIGHT - FOOTER_H + 22), footer_left, fill=(148, 163, 184), font=font_footer)

    # Right footer item - dynamically measured to avoid ANY border escaping!
    footer_right = "TOUCH GRASS SAFELY  //  TabPFN + TEMPORAL"
    tb_fr = draw_footer.textbbox((0, 0), footer_right, font=font_footer)
    fr_w = tb_fr[2] - tb_fr[0]
    draw_footer.text((WIDTH - fr_w - 90, HEIGHT - FOOTER_H + 22), footer_right, fill=(52, 211, 153), font=font_footer)

    # Save Output
    base.save(OUTPUT_PNG, quality=96)
    print(f"Thumbnail rendered successfully to {OUTPUT_PNG} ({OUTPUT_PNG.stat().st_size} bytes)")

if __name__ == "__main__":
    draw_thumbnail()
