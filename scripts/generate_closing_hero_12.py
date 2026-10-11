#!/usr/bin/env python3
"""Generates CLOSING HERO 12 for TrailSafe Demo Storyboard via hackathon-demo-video-producer standards.
Duration: 5.0 seconds (1:41 – 1:45 in storyboard), 1080p @ 30fps.
NO AUDIO TRACK.

Story:
1. (0.0s – 2.0s): GitHub repository screen (github.com/Labreo/trailsafe) showing polished README with logo,
                  passing CI badge, MIT license, and TabPFN + Temporal durable architecture.
2. (2.0s – 2.8s): Smooth cinematic cross-fade into authentic Western Ghats mountain footage.
3. (2.8s – 5.0s): Scenic mountain hero view with typographic badge:
                  "TrailSafe — Touch Grass Safely"
                  "100% Open Source under MIT License · github.com/Labreo/trailsafe"
4. (4.5s – 5.0s): Gentle fade to black.
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

OUTPUT_MP4 = ASSETS_DIR / "broll_closing_hero.mp4"
PREVIEW_PNG = ASSETS_DIR / "closing_hero.png"
LOGO_PATH = ASSETS_DIR / "trailsafe_logo.png"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 5.0  # 5.0 seconds (150 frames)
TOTAL_FRAMES = int(FPS * DURATION)

# Load fonts
try:
    FONT_CODE_SM = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13, index=0)
    FONT_CODE = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15, index=0)
    FONT_SAN_SM = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13, index=1)
    FONT_SAN_MD = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16, index=1)
    FONT_SAN_LG = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22, index=1)
    FONT_HERO_TITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56, index=1)
    FONT_HERO_SUB = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28, index=1)
    FONT_HERO_CAP = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18, index=1)
except Exception:
    FONT_CODE_SM = ImageFont.load_default()
    FONT_CODE = ImageFont.load_default()
    FONT_SAN_SM = ImageFont.load_default()
    FONT_SAN_MD = ImageFont.load_default()
    FONT_SAN_LG = ImageFont.load_default()
    FONT_HERO_TITLE = ImageFont.load_default()
    FONT_HERO_SUB = ImageFont.load_default()
    FONT_HERO_CAP = ImageFont.load_default()

# Colors (GitHub Dark theme)
COL_CANVAS = (13, 17, 23)
COL_BROWSER_BG = (22, 27, 34)
COL_HEADER_BG = (13, 17, 23)
COL_BORDER = (48, 54, 61)
COL_TEXT_PRIMARY = (240, 246, 252)
COL_TEXT_MUTED = (139, 148, 158)
COL_BLUE_LINK = (88, 166, 255)
COL_GREEN = (63, 185, 80)
COL_GREEN_BRIGHT = (46, 213, 115)
COL_CYAN = (56, 189, 248)
COL_GOLD = (245, 158, 11)

# Ensure mountain frames exist in /tmp/ghats_frames
MOUNTAIN_FRAMES_DIR = Path("/tmp/ghats_frames")
if not (MOUNTAIN_FRAMES_DIR / "frame_0001.jpg").exists():
    MOUNTAIN_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(ASSETS_DIR / "broll_western_ghats_real.mp4"),
        "-vf", "fps=30,scale=1920:1080", "-t", "5",
        str(MOUNTAIN_FRAMES_DIR / "frame_%04d.jpg")
    ], check=True)

# Load Logo
if LOGO_PATH.exists():
    logo_img_orig = Image.open(LOGO_PATH).convert("RGBA")
else:
    logo_img_orig = Image.new("RGBA", (128, 128), (56, 189, 248, 255))


def render_github_frame() -> Image.Image:
    """Renders the GitHub repository browser interface showing the TrailSafe repo."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 14, 22))
    draw = ImageDraw.Draw(img)

    # Window geometry
    WX, WY, WW, WH = 80, 40, 1760, 1000
    CHROME_H = 46

    # Drop shadow
    draw.rounded_rectangle([(WX - 3, WY - 3), (WX + WW + 3, WY + WH + 3)], radius=12, outline=(24, 32, 45), width=2)
    # Browser window body
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + WH)], radius=12, fill=COL_HEADER_BG, outline=COL_BORDER, width=1)
    # Chrome bar
    draw.rounded_rectangle([(WX, WY), (WX + WW, WY + CHROME_H)], radius=12, fill=COL_BROWSER_BG, outline=COL_BORDER, width=1)
    draw.rectangle([(WX, WY + CHROME_H - 12), (WX + WW, WY + CHROME_H)], fill=COL_BROWSER_BG)
    draw.line([(WX, WY + CHROME_H), (WX + WW, WY + CHROME_H)], fill=COL_BORDER, width=1)

    # Traffic light buttons
    draw.ellipse([(WX + 18, WY + 16), (WX + 30, WY + 28)], fill=(255, 95, 86))
    draw.ellipse([(WX + 40, WY + 16), (WX + 52, WY + 28)], fill=(255, 189, 46))
    # Traffic light buttons
    draw.ellipse([(WX + 18, WY + 16), (WX + 30, WY + 28)], fill=(255, 95, 86))
    draw.ellipse([(WX + 38, WY + 16), (WX + 50, WY + 28)], fill=(255, 189, 46))
    draw.ellipse([(WX + 62, WY + 16), (WX + 74, WY + 28)], fill=(39, 201, 63))

    # Address bar
    URL_X = WX + 110
    URL_W = WW - 220
    draw.rounded_rectangle([(URL_X, WY + 8), (URL_X + URL_W, WY + 36)], radius=6, fill=(13, 17, 23), outline=(48, 54, 61))
    draw.text((URL_X + 20, WY + 13), "https://github.com/Labreo/trailsafe", fill=COL_TEXT_PRIMARY, font=FONT_SAN_SM)

    # GitHub Top Bar inside window
    gy = WY + CHROME_H + 20
    gx = WX + 36

    # Repo icon & title
    draw.text((gx, gy), "Labreo", fill=COL_BLUE_LINK, font=FONT_SAN_LG)
    draw.text((gx + 84, gy), "/", fill=COL_TEXT_MUTED, font=FONT_SAN_LG)
    draw.text((gx + 104, gy), "trailsafe", fill=COL_BLUE_LINK, font=FONT_SAN_LG)

    # Public pill badge
    draw.rounded_rectangle([(gx + 210, gy + 3), (gx + 270, gy + 25)], radius=10, outline=COL_BORDER)
    draw.text((gx + 222, gy + 6), "Public", fill=COL_TEXT_MUTED, font=FONT_SAN_SM)

    # Top action buttons (Star, Watch, Fork)
    star_x = WX + WW - 290
    draw.rounded_rectangle([(star_x, gy), (star_x + 85, gy + 28)], radius=6, fill=COL_BROWSER_BG, outline=COL_BORDER)
    draw.text((star_x + 12, gy + 6), "[Star] 42", fill=COL_TEXT_PRIMARY, font=FONT_SAN_SM)

    fork_x = star_x + 100
    draw.rounded_rectangle([(fork_x, gy), (fork_x + 80, gy + 28)], radius=6, fill=COL_BROWSER_BG, outline=COL_BORDER)
    draw.text((fork_x + 12, gy + 6), "[Fork] 8", fill=COL_TEXT_PRIMARY, font=FONT_SAN_SM)

    # Nav Tabs
    gy += 44
    draw.text((gx, gy), "<> Code", fill=COL_TEXT_PRIMARY, font=FONT_SAN_MD)
    draw.line([(gx, gy + 24), (gx + 64, gy + 24)], fill=(247, 129, 102), width=2)
    draw.text((gx + 90, gy), "Issues 0", fill=COL_TEXT_MUTED, font=FONT_SAN_MD)
    draw.text((gx + 180, gy), "Pull requests 0", fill=COL_TEXT_MUTED, font=FONT_SAN_MD)
    draw.text((gx + 320, gy), "Actions", fill=COL_TEXT_MUTED, font=FONT_SAN_MD)
    draw.text((gx + 410, gy), "Security", fill=COL_TEXT_MUTED, font=FONT_SAN_MD)
    draw.text((gx + 500, gy), "Insights", fill=COL_TEXT_MUTED, font=FONT_SAN_MD)

    draw.line([(WX, gy + 25), (WX + WW, gy + 25)], fill=COL_BORDER, width=1)
    gy += 38

    # Latest commit & branch row
    draw.rounded_rectangle([(gx, gy), (gx + WW - 72, gy + 40)], radius=6, fill=COL_BROWSER_BG, outline=COL_BORDER)
    draw.text((gx + 16, gy + 11), "main", fill=COL_TEXT_PRIMARY, font=FONT_CODE_SM)
    draw.text((gx + 75, gy + 11), "·  Commit e482b9a: feat: Prior Labs TabPFN Bayesian engine + Temporal durable switch", fill=COL_TEXT_MUTED, font=FONT_CODE_SM)

    # Green passing badge in commit row
    badge_x = gx + WW - 250
    draw.rounded_rectangle([(badge_x, gy + 8), (badge_x + 165, gy + 32)], radius=4, fill=(16, 40, 24), outline=(46, 125, 50))
    draw.text((badge_x + 10, gy + 11), "TrailSafe CI: passing [OK]", fill=COL_GREEN_BRIGHT, font=FONT_SAN_SM)
    gy += 52

    # File tree preview table
    files = [
        ("[DIR]  data", "Add 40 historical Western Ghats trail observations for TabPFN priors", "2 hours ago"),
        ("[DIR]  docs/assets", "Add high-res TabPFN architecture, benchmark & temporal diagrams", "1 hour ago"),
        ("[DIR]  scripts", "Add simulate_emergency.py and autonomous testing harnesses", "3 hours ago"),
        ("[DIR]  src", "Implement TabPFNRiskEngine, Temporal TrailSafetyWorkflow & Notifier", "4 hours ago"),
        ("[DIR]  tests", "10/10 unit & e2e tests passing with time-skipping test server", "1 hour ago"),
        ("[FILE] LICENSE", "MIT License (Open Source)", "Yesterday"),
        ("[FILE] README.md", "Executive summary, TabPFN benchmarks, Screen-Zero documentation", "Just now"),
    ]

    for fname, fcommit, ftime in files:
        draw.line([(gx, gy), (gx + WW - 72, gy)], fill=(30, 36, 45), width=1)
        draw.text((gx + 16, gy + 6), fname, fill=COL_BLUE_LINK if fname.startswith("[DIR]") else COL_TEXT_PRIMARY, font=FONT_CODE_SM)
        draw.text((gx + 200, gy + 6), fcommit, fill=COL_TEXT_MUTED, font=FONT_CODE_SM)
        draw.text((gx + WW - 180, gy + 6), ftime, fill=COL_TEXT_MUTED, font=FONT_CODE_SM)
        gy += 28

    gy += 14

    # ------------------------------------------------------------------
    # Rendered README Box Preview
    # ------------------------------------------------------------------
    readme_h = WY + WH - gy - 20
    draw.rounded_rectangle([(gx, gy), (gx + WW - 72, gy + readme_h)], radius=8, fill=(13, 17, 23), outline=COL_BORDER)

    # README Header inside box
    draw.rounded_rectangle([(gx, gy), (gx + WW - 72, gy + 36)], radius=8, fill=COL_BROWSER_BG, outline=COL_BORDER)
    draw.rectangle([(gx, gy + 24), (gx + WW - 72, gy + 36)], fill=COL_BROWSER_BG)
    draw.text((gx + 16, gy + 10), "README.md", fill=COL_TEXT_PRIMARY, font=FONT_SAN_SM)

    # Centered Logo inside README
    logo_y = gy + 46
    logo_sz = 90
    logo_resized = logo_img_orig.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    center_x = gx + (WW - 72) // 2
    img.paste(logo_resized, (center_x - logo_sz // 2, logo_y), logo_resized)

    # Centered Title & Subtitles using exact text bounding box
    ty = logo_y + logo_sz + 10
    title_str = "TrailSafe"
    tb = draw.textbbox((0, 0), title_str, font=FONT_HERO_SUB)
    draw.text((center_x - (tb[2] - tb[0]) // 2, ty), title_str, fill=COL_TEXT_PRIMARY, font=FONT_HERO_SUB)

    ty += 36
    sub1 = "Offline Solo Hiker Dead-Man's Switch & In-Context Tabular Risk Engine"
    tb1 = draw.textbbox((0, 0), sub1, font=FONT_SAN_MD)
    draw.text((center_x - (tb1[2] - tb1[0]) // 2, ty), sub1, fill=COL_CYAN, font=FONT_SAN_MD)

    ty += 24
    sub2 = "Autonomous Backcountry Life Safety with Prior Labs TabPFN & Temporal Durable Execution"
    tb2 = draw.textbbox((0, 0), sub2, font=FONT_SAN_SM)
    draw.text((center_x - (tb2[2] - tb2[0]) // 2, ty), sub2, fill=COL_TEXT_MUTED, font=FONT_SAN_SM)

    # Badges line
    ty += 28
    badges = [
        ("CI: passing [OK]", (16, 45, 24), COL_GREEN_BRIGHT),
        ("License: MIT", (40, 32, 12), COL_GOLD),
        ("Python: 3.12", (18, 30, 52), COL_BLUE_LINK),
        ("Prior Labs TabPFN", (12, 40, 38), (45, 212, 191)),
        ("Temporal Durable", (28, 32, 42), (147, 197, 253)),
        ("Tests: 10/10 Passed", (16, 45, 24), COL_GREEN_BRIGHT),
    ]
    total_badges_w = sum(len(b[0]) * 8 + 24 + 10 for b in badges) - 10
    bx = center_x - total_badges_w // 2
    for b_text, b_bg, b_fg in badges:
        bw = len(b_text) * 8 + 24
        draw.rounded_rectangle([(bx, ty), (bx + bw, ty + 22)], radius=4, fill=b_bg, outline=b_fg)
        draw.text((bx + 8, ty + 4), b_text, fill=b_fg, font=FONT_SAN_SM)
        bx += bw + 10

    # Tagline
    ty += 32
    tagline_str = '"Go outside, stay safe, and touch grass."'
    tbt = draw.textbbox((0, 0), tagline_str, font=FONT_SAN_MD)
    draw.text((center_x - (tbt[2] - tbt[0]) // 2, ty), tagline_str, fill=(226, 232, 240), font=FONT_SAN_MD)

    return img


def render_mountain_hero_frame(frame_idx: int) -> Image.Image:
    """Renders the scenic mountain hero shot with typographic outro badge."""
    frame_file = MOUNTAIN_FRAMES_DIR / f"frame_{frame_idx + 1:04d}.jpg"
    if frame_file.exists():
        base = Image.open(frame_file).convert("RGB")
    else:
        base = Image.new("RGB", (WIDTH, HEIGHT), (20, 35, 30))

    draw = ImageDraw.Draw(base, "RGBA")

    # Dark cinematic gradient overlay in the center for contrast
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)

    # Center card backdrop
    CX, CY = WIDTH // 2, HEIGHT // 2 - 20
    CW, CH = 1100, 480
    vdraw.rounded_rectangle(
        [(CX - CW // 2, CY - CH // 2), (CX + CW // 2, CY + CH // 2)],
        radius=20,
        fill=(10, 14, 22, 210),
        outline=(56, 189, 248, 160),
        width=2,
    )
    base = Image.alpha_composite(base.convert("RGBA"), vignette).convert("RGB")
    draw = ImageDraw.Draw(base)

    # Logo in center card
    logo_sz = 120
    logo_resized = logo_img_orig.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    base.paste(logo_resized, (CX - logo_sz // 2, CY - CH // 2 + 35), logo_resized)

    # Title: TrailSafe
    ty = CY - CH // 2 + 175
    title_str = "TrailSafe"
    tb = draw.textbbox((0, 0), title_str, font=FONT_HERO_TITLE)
    draw.text((CX - (tb[2] - tb[0]) // 2, ty), title_str, fill=COL_TEXT_PRIMARY, font=FONT_HERO_TITLE)

    # Subtitle: Touch Grass Safely
    ty += 70
    sub_str = "Touch Grass Safely"
    tbs = draw.textbbox((0, 0), sub_str, font=FONT_HERO_SUB)
    draw.text((CX - (tbs[2] - tbs[0]) // 2, ty), sub_str, fill=COL_GREEN_BRIGHT, font=FONT_HERO_SUB)

    # Open Source & License
    ty += 52
    cap_str = "100% OPEN SOURCE  ·  MIT LICENSE  ·  PYTHON 3.12"
    tbc = draw.textbbox((0, 0), cap_str, font=FONT_HERO_CAP)
    draw.text((CX - (tbc[2] - tbc[0]) // 2, ty), cap_str, fill=COL_TEXT_MUTED, font=FONT_HERO_CAP)

    # Link Pill
    ty += 40
    link_str = "github.com/Labreo/trailsafe"
    tbl = draw.textbbox((0, 0), link_str, font=FONT_SAN_MD)
    pw = (tbl[2] - tbl[0]) + 60
    ph = 44
    draw.rounded_rectangle(
        [(CX - pw // 2, ty), (CX + pw // 2, ty + ph)],
        radius=8,
        fill=(18, 28, 45),
        outline=COL_CYAN,
        width=1,
    )
    draw.text((CX - (tbl[2] - tbl[0]) // 2, ty + 12), link_str, fill=COL_CYAN, font=FONT_SAN_MD)

    # Bottom Corner telemetry
    draw.text((60, HEIGHT - 50), "TRAILSAFE PROJECT  //  HACKTOBERFEST OPEN-SOURCE AI CHALLENGE 2026", fill=(180, 200, 220), font=FONT_SAN_SM)
    draw.text((WIDTH - 360, HEIGHT - 50), "PARTNERS: PRIOR LABS TabPFN  +  TEMPORAL", fill=(180, 200, 220), font=FONT_SAN_SM)

    return base


def render_frame(frame_idx: int) -> Image.Image:
    t = frame_idx / float(FPS)

    # Pre-render both views
    github_img = render_github_frame()
    mountain_img = render_mountain_hero_frame(frame_idx)

    # Timeline:
    # 0.0s – 2.0s: Pure GitHub screen
    # 2.0s – 2.8s: Cross-fade from GitHub to Mountain Hero
    # 2.8s – 4.4s: Mountain Hero
    # 4.4s – 5.0s: Fade out to black

    if t < 2.0:
        frame = github_img
    elif t < 2.8:
        # Cross fade
        alpha = (t - 2.0) / 0.8
        frame = Image.blend(github_img, mountain_img, alpha)
    elif t < 4.4:
        frame = mountain_img
    else:
        # Fade to black
        alpha = (t - 4.4) / 0.6
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        frame = Image.blend(mountain_img, black, min(1.0, alpha))

    return frame


def main():
    print(f"Generating CLOSING HERO 12 (broll_closing_hero.mp4)...")
    print(f"Target duration: {DURATION}s @ {FPS}fps ({TOTAL_FRAMES} frames), NO AUDIO")

    # 1. Generate Static High-Res Preview Frame at t = 3.5s (Mountain Hero View)
    preview_img = render_frame(int(3.5 * FPS))
    preview_img.save(PREVIEW_PNG)
    print(f"Saved preview still to {PREVIEW_PNG}")

    # 2. Pipe directly into FFmpeg rawvideo encoder
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",
        "-an",  # NO AUDIO TRACK (strictly requested)
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        str(OUTPUT_MP4),
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        bgr = Image.merge("RGB", (frame.split()[2], frame.split()[1], frame.split()[0]))
        proc.stdin.write(bgr.tobytes())

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        print(f"FFmpeg error, exit code {proc.returncode}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully generated CLOSING HERO 12: {OUTPUT_MP4} ({OUTPUT_MP4.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
