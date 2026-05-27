"""
Generates 3 branded LinkedIn carousel slide images for Growth Lab Co.
Inputs: .tmp/linkedin_content.json
Outputs: .tmp/slide_1.png, .tmp/slide_2.png, .tmp/slide_3.png
Usage: python3 tools/generate_infographic.py
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Brand colours
MIDNIGHT_BASE = "#181840"
ELECTRIC_VIOLET = "#A070F8"
SOFT_VIOLET = "#9878F0"
CLEAN_WHITE = "#F8F8F8"
MIDNIGHT_SHADOW = "#181038"

# LinkedIn carousel dimensions (1:1 square, high res)
W, H = 1080, 1080

CONTENT_FILE = ".tmp/linkedin_content.json"
LOGO_FILE = ".tmp/logomark.png"
FONT_DIR = ".tmp/fonts"


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def load_font(size, bold=False):
    candidates = []
    if bold:
        candidates = [
            os.path.expanduser("~/Library/Fonts/SpaceGrotesk-Bold.otf"),
            os.path.join(FONT_DIR, "SpaceGrotesk-Bold.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        candidates = [
            os.path.expanduser("~/Library/Fonts/SpaceGrotesk-Regular.otf"),
            os.path.join(FONT_DIR, "SpaceGrotesk-Regular.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_background(draw, with_glow=True):
    draw.rectangle([0, 0, W, H], fill=hex_to_rgb(MIDNIGHT_BASE))
    if with_glow:
        # Subtle violet glow in top-right corner
        for i in range(180, 0, -10):
            alpha_color = tuple(list(hex_to_rgb(SOFT_VIOLET)) + [int(i * 0.15)])
            draw.ellipse([W - i*2, -i, W + i, i*2], fill=hex_to_rgb(MIDNIGHT_SHADOW))


def add_logo(img, size=70, position=(52, 52)):
    try:
        logo = Image.open(LOGO_FILE).convert("RGBA")
        logo = logo.resize((size, size), Image.LANCZOS)
        img.paste(logo, position, logo)
    except Exception:
        pass


def draw_accent_bar(draw, y, width=120, height=5):
    draw.rounded_rectangle([52, y, 52 + width, y + height], radius=3, fill=hex_to_rgb(ELECTRIC_VIOLET))


def wrap_text(draw, text, font, max_width, x, y, fill, line_spacing=8):
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def make_slide_1(slides_data):
    img = Image.new("RGB", (W, H), hex_to_rgb(MIDNIGHT_BASE))
    draw = ImageDraw.Draw(img)
    draw_background(draw)
    add_logo(img)

    # "Growth Lab Co." small label top right
    font_label = load_font(24)
    draw.text((W - 220, 68), "Growth Lab Co.", font=font_label, fill=hex_to_rgb(SOFT_VIOLET))

    # Accent bar
    draw_accent_bar(draw, y=H // 2 - 120)

    # Headline
    headline = slides_data["slide_1"]["headline"]
    font_headline = load_font(72, bold=True)
    wrap_text(draw, headline, font_headline, W - 104, 52, H // 2 - 100, hex_to_rgb(CLEAN_WHITE), line_spacing=12)

    # Subheading
    subheading = slides_data["slide_1"]["subheading"]
    font_sub = load_font(34)
    wrap_text(draw, subheading, font_sub, W - 104, 52, H // 2 + 110, hex_to_rgb(SOFT_VIOLET), line_spacing=10)

    # Slide number
    font_num = load_font(22)
    draw.text((W - 80, H - 60), "1 / 3", font=font_num, fill=hex_to_rgb(SOFT_VIOLET))

    img.save(".tmp/slide_1.png")
    print("✓ slide_1.png")


def make_slide_2(slides_data):
    img = Image.new("RGB", (W, H), hex_to_rgb(MIDNIGHT_BASE))
    draw = ImageDraw.Draw(img)
    draw_background(draw)
    add_logo(img)

    font_label = load_font(24)
    draw.text((W - 220, 68), "Growth Lab Co.", font=font_label, fill=hex_to_rgb(SOFT_VIOLET))

    draw_accent_bar(draw, y=200)

    # Headline
    headline = slides_data["slide_2"]["headline"]
    font_headline = load_font(52, bold=True)
    y = wrap_text(draw, headline, font_headline, W - 104, 52, 220, hex_to_rgb(CLEAN_WHITE), line_spacing=10)

    # Bullets
    bullets = slides_data["slide_2"]["bullets"]
    font_bullet = load_font(34)
    y += 60
    for bullet in bullets:
        # Violet dot
        draw.ellipse([52, y + 14, 68, y + 30], fill=hex_to_rgb(ELECTRIC_VIOLET))
        y = wrap_text(draw, bullet, font_bullet, W - 130, 82, y, hex_to_rgb(CLEAN_WHITE), line_spacing=8)
        y += 32

    font_num = load_font(22)
    draw.text((W - 80, H - 60), "2 / 3", font=font_num, fill=hex_to_rgb(SOFT_VIOLET))

    img.save(".tmp/slide_2.png")
    print("✓ slide_2.png")


def make_slide_3(slides_data):
    img = Image.new("RGB", (W, H), hex_to_rgb(MIDNIGHT_SHADOW))
    draw = ImageDraw.Draw(img)
    draw_background(draw)
    add_logo(img)

    font_label = load_font(24)
    draw.text((W - 220, 68), "Growth Lab Co.", font=font_label, fill=hex_to_rgb(SOFT_VIOLET))

    # Accent bar centred vertically
    draw_accent_bar(draw, y=H // 2 - 80, width=W - 104)

    # Closing statement
    statement = slides_data["slide_3"]["statement"]
    font_statement = load_font(62, bold=True)
    wrap_text(draw, statement, font_statement, W - 104, 52, H // 2 - 60, hex_to_rgb(CLEAN_WHITE), line_spacing=12)

    # CTA
    cta = slides_data["slide_3"]["cta"]
    font_cta = load_font(30)
    wrap_text(draw, cta, font_cta, W - 104, 52, H // 2 + 160, hex_to_rgb(ELECTRIC_VIOLET), line_spacing=8)

    font_num = load_font(22)
    draw.text((W - 80, H - 60), "3 / 3", font=font_num, fill=hex_to_rgb(SOFT_VIOLET))

    img.save(".tmp/slide_3.png")
    print("✓ slide_3.png")


def download_fonts():
    # Fonts are installed via: brew install --cask font-space-grotesk
    # No download needed — load_font() picks them up from ~/Library/Fonts/
    os.makedirs(FONT_DIR, exist_ok=True)


if __name__ == "__main__":
    download_fonts()

    with open(CONTENT_FILE) as f:
        content = json.load(f)

    slides = content["slides"]
    make_slide_1(slides)
    make_slide_2(slides)
    make_slide_3(slides)

    print("✓ All 3 slides generated in .tmp/")
