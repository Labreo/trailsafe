#!/usr/bin/env python3
"""Generates a high-converting 16:9 YouTube / Video Demo thumbnail for TrailSafe.
Resolution: 1920x1080 (Full HD, 16:9 standard).
Saves to: docs/assets/youtube_thumbnail.png
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "docs" / "assets"
OUTPUT_PNG = ASSETS_DIR / "youtube_thumbnail.png"
LOGO_PATH = ASSETS_DIR / "trailsafe_logo.png"
MOUNTAIN_FRAMES_DIR = Path("/tmp/ghats_frames")

WIDTH, HEIGHT = 1920, 1080

def get_base_scenery():
    # Check for real mountain background frame
    frame_file = MOUNTAIN_FRAMES_DIR / "frame_0060.jpg"
    if frame_file.exists():
        base = Image.open(frame_file).convert("RGB")
        base = base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    else:
        # Gradient background
        base = Image.new("RGB", (WIDTH, HEIGHT), (10, 20, 18))
        draw = ImageDraw.Draw(base)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(10 + 15 * ratio)
            g = int(22 + 25 * ratio)
            b = int(25 + 30 * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return base

def draw_thumbnail():
    base = get_base_scenery()

    # Dark cinematic vignette / gradient overlay to ensure perfect text legibility
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Dark horizontal gradient from left to right (heavier on left for typography)
    for x in range(WIDTH):
        alpha = int(230 - 80 * (x / WIDTH))  # 230 on left, 150 on right
        odraw.line([(x, 0), (x, HEIGHT)], fill=(8, 12, 18, alpha))

    # Top & bottom letterbox shadow
    for y in range(160):
        alpha = int(200 * (1.0 - y / 160.0))
        odraw.line([(0, y), (WIDTH, y)], fill=(4, 8, 12, alpha))
        odraw.line([(0, HEIGHT - 1 - y), (WIDTH, HEIGHT - 1 - y)], fill=(4, 8, 12, alpha))

    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base, "RGBA")

    # Load high-impact fonts with proper lowercase rendering
    try:
        font_super = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 94)
        font_subhead = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 44)
        font_pill = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
        font_body = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
        font_kicker = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20, index=0)
        font_footer = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 19)
    except Exception:
        font_super = ImageFont.load_default()
        font_subhead = ImageFont.load_default()
        font_pill = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_kicker = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Left content positioning
    LEFT_X = 110

    # 1. Category / Topic Kicker in a sleek top badge
    kicker_text = "HACKTOBERFEST 2026 // OPEN-SOURCE AI CHALLENGE"
    tb_k = draw.textbbox((0, 0), kicker_text, font=font_kicker)
    kw = tb_k[2] - tb_k[0]
    draw.rounded_rectangle(
        [(LEFT_X - 12, 70), (LEFT_X + kw + 16, 114)],
        radius=6,
        fill=(15, 23, 42, 230),
        outline=(56, 189, 248, 180),
        width=1
    )
    draw.text((LEFT_X, 80), kicker_text, fill=(56, 189, 248, 255), font=font_kicker)

    # 2. Main Title: TRAILSAFE (Huge, Bold, Emerald/Cyan gradient tone)
    title_text = "TRAILSAFE"
    # Soft glow behind title
    for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3), (0, 4)]:
        draw.text((LEFT_X + offset[0], 140 + offset[1]), title_text, fill=(0, 0, 0, 200), font=font_super)
    draw.text((LEFT_X, 140), title_text, fill=(255, 255, 255), font=font_super)

    # 3. Punchy Tagline / Hook: TOUCH GRASS SAFELY (Bright Emerald Green)
    tag_text = "TOUCH GRASS SAFELY"
    draw.text((LEFT_X, 252), tag_text, fill=(52, 211, 153), font=font_subhead)

    # 4. Core Hook Subhead
    sub_y = 330
    hook_box = "Zero Cell Coverage? You're Still Protected."
    draw.text((LEFT_X, sub_y), hook_box, fill=(226, 232, 240), font=font_pill)

    # 5. Three Key Technical Feature Badges (Pills)
    pills = [
        ("PRIOR LABS TabPFN", "Bayesian In-Context AI", (16, 185, 129)),
        ("TEMPORAL IO", "Durable Dead Man's Switch", (56, 189, 248)),
        ("100% OFFLINE", "Zero Cloud Reliance", (245, 158, 11)),
    ]

    pill_y = 410
    for header, desc, col in pills:
        # Pill card
        card_w, card_h = 580, 84
        draw.rounded_rectangle(
            [(LEFT_X, pill_y), (LEFT_X + card_w, pill_y + card_h)],
            radius=12,
            fill=(15, 23, 42, 220),
            outline=(col[0], col[1], col[2], 180),
            width=2
        )
        # Left color bar
        draw.rounded_rectangle(
            [(LEFT_X + 4, pill_y + 4), (LEFT_X + 14, pill_y + card_h - 4)],
            radius=4,
            fill=(col[0], col[1], col[2], 255)
        )
        # Text in card
        draw.text((LEFT_X + 32, pill_y + 14), header, fill=(col[0], col[1], col[2]), font=font_pill)
        draw.text((LEFT_X + 32, pill_y + 46), desc, fill=(203, 213, 225), font=font_body)

        pill_y += 105

    # 6. Bottom metadata badge
    meta_box_y = 750
    draw.rounded_rectangle(
        [(LEFT_X, meta_box_y), (LEFT_X + 580, meta_box_y + 64)],
        radius=8,
        fill=(10, 16, 28, 200),
        outline=(56, 189, 248, 80),
        width=1
    )
    draw.text((LEFT_X + 24, meta_box_y + 18), "17.9 mL MAE Fluid Deficit Forecast  ·  34.2 mL Random Forest", fill=(148, 163, 184), font=font_body)

    # 7. Right Side: Big TrailSafe Logo with Glassmorphic HUD Badge
    if LOGO_PATH.exists():
        logo_raw = Image.open(LOGO_PATH).convert("RGBA")
        logo_size = 460
        logo_scaled = logo_raw.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        RX = WIDTH - 580
        RY = HEIGHT // 2 - 250

        # Backplate for logo
        hud_w, hud_h = 520, 560
        hud_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(hud_overlay)
        hdraw.rounded_rectangle(
            [(RX - 20, RY - 20), (RX + hud_w - 20, RY + hud_h - 20)],
            radius=24,
            fill=(13, 20, 36, 190),
            outline=(52, 211, 153, 140),
            width=2
        )
        base = Image.alpha_composite(base.convert("RGBA"), hud_overlay).convert("RGB")

        # Paste logo
        base.paste(logo_scaled, (RX + 10, RY + 10), logo_scaled)

        # Badge under logo
        draw_after = ImageDraw.Draw(base, "RGBA")
        badge_y = RY + logo_size + 25
        badge_text = "SAR TELEMETRY PROTOCOL"
        tb = draw_after.textbbox((0, 0), badge_text, font=font_kicker)
        tw = tb[2] - tb[0]
        draw_after.rounded_rectangle(
            [(RX + (hud_w - tw) // 2 - 40, badge_y), (RX + (hud_w + tw) // 2 - 20, badge_y + 40)],
            radius=6,
            fill=(52, 211, 153, 30),
            outline=(52, 211, 153, 200),
            width=1
        )
        draw_after.text((RX + (hud_w - tw) // 2 - 30, badge_y + 8), badge_text, fill=(52, 211, 153), font=font_kicker)

    # 8. Bottom Footer Bar
    draw_final = ImageDraw.Draw(base, "RGBA")
    draw_final.rectangle([(0, HEIGHT - 65), (WIDTH, HEIGHT)], fill=(4, 7, 12, 240))
    draw_final.line([(0, HEIGHT - 65), (WIDTH, HEIGHT - 65)], fill=(56, 189, 248, 80), width=1)
    draw_final.text((LEFT_X, HEIGHT - 44), "GITHUB: github.com/Labreo/trailsafe  ·  MIT LICENSE", fill=(148, 163, 184), font=font_footer)
    draw_final.text((WIDTH - 550, HEIGHT - 44), "TOUCH GRASS SAFELY // BUILT WITH PRIOR LABS TabPFN", fill=(52, 211, 153), font=font_footer)

    # Save Thumbnail
    base.save(OUTPUT_PNG, quality=95)
    print(f"Thumbnail saved successfully to: {OUTPUT_PNG} ({OUTPUT_PNG.stat().st_size} bytes)")

if __name__ == "__main__":
    draw_thumbnail()
