#!/usr/bin/env python3
"""Generate the dark-mode README screenshots.

The README graphics are generated from code so they can be refreshed without
manual image editing. They depict the current dark-mode app panel and settings
layout while avoiding local desktop state in committed documentation assets.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "images"
W, H = 2560, 1600

BG = (18, 20, 24)
PANEL = (31, 34, 40)
PANEL_2 = (39, 43, 51)
BORDER = (68, 73, 84)
TEXT = (238, 240, 244)
MUTED = (167, 174, 186)
BLUE = (75, 141, 245)
PINK = (224, 10, 99)
GREEN = (83, 190, 128)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[str] = []
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/SFNS-Bold.ttf",
        ]
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill=TEXT, bold: bool = False, anchor=None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def base_image() -> Image.Image:
    image = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(image)
    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill=(25, 28, 34), width=1)
    for y in range(0, H, 80):
        draw.line((0, y, W, y), fill=(25, 28, 34), width=1)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    rounded(shadow_draw, (180, 130, 2380, 1470), 44, (0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    image.alpha_composite(shadow)

    draw = ImageDraw.Draw(image)
    rounded(draw, (180, 130, 2380, 1470), 44, PANEL, BORDER, 2)
    return image


def logo(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    size = int(164 * scale)
    rounded(
        draw,
        (cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2),
        int(34 * scale),
        (22, 26, 34),
        (76, 84, 101),
        2,
    )

    rounded(
        draw,
        (cx - int(55 * scale), cy - int(50 * scale), cx + int(47 * scale), cy + int(28 * scale)),
        int(18 * scale),
        PINK,
    )
    draw.polygon(
        [
            (cx - int(18 * scale), cy + int(26 * scale)),
            (cx - int(2 * scale), cy + int(54 * scale)),
            (cx + int(9 * scale), cy + int(25 * scale)),
        ],
        fill=PINK,
    )
    label(draw, (cx - int(30 * scale), cy - int(30 * scale)), "A", int(48 * scale), (255, 255, 255), True)
    label(draw, (cx + int(8 * scale), cy - int(29 * scale)), "文", int(42 * scale), (255, 255, 255), True)
    draw.line(
        (cx - int(45 * scale), cy + int(60 * scale), cx + int(42 * scale), cy + int(60 * scale)),
        fill=BLUE,
        width=max(2, int(9 * scale)),
    )
    draw.polygon(
        [
            (cx + int(42 * scale), cy + int(60 * scale)),
            (cx + int(22 * scale), cy + int(46 * scale)),
            (cx + int(22 * scale), cy + int(74 * scale)),
        ],
        fill=BLUE,
    )


def window_chrome(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, selected: str) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 24, PANEL, BORDER, 2)
    draw.rectangle((x0, y0 + 58, x1, y0 + 59), fill=BORDER)
    for index, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse((x0 + 24 + index * 32, y0 + 22, x0 + 42 + index * 32, y0 + 40), fill=color)
    label(draw, (x0 + 125, y0 + 20), title, 22, TEXT, True)

    tabs = [("Translate", x1 - 330, x1 - 185), ("Settings", x1 - 180, x1 - 55)]
    for name, left, right in tabs:
        rounded(draw, (left, y0 + 15, right, y0 + 45), 10, (52, 57, 67) if name == selected else PANEL_2, BORDER, 1)
        label(draw, (left + 22, y0 + 22), name, 17, TEXT if name == selected else MUTED)


def translate_panel(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    window_chrome(draw, (x, y, x + width, y + height), "BarTranslateACO", "Translate")
    rounded(draw, (x + 35, y + 92, x + width - 35, y + 365), 18, (247, 248, 251), (205, 210, 220), 1)
    label(draw, (x + 65, y + 125), "Good evening", 38, (35, 39, 47), True)
    label(draw, (x + 65, y + 190), "Spanish", 21, (91, 99, 114))
    draw.line((x + 65, y + 232, x + width - 65, y + 232), fill=(215, 219, 227), width=2)
    label(draw, (x + 65, y + 272), "Buenas noches", 39, (25, 29, 36), True)
    rounded(draw, (x + width - 170, y + 305, x + width - 65, y + 342), 9, (231, 239, 255), (190, 210, 245), 1)
    label(draw, (x + width - 143, y + 313), "Copy", 20, (55, 113, 210), True)

    rounded(draw, (x + 35, y + 395, x + width - 35, y + 552), 18, PANEL_2, BORDER, 1)
    label(draw, (x + 65, y + 430), "⌥ + ; toggles the panel", 28, TEXT, True)
    label(draw, (x + 65, y + 485), "Auto-focus and optional clipboard paste keep translation fast.", 23, MUTED)


def settings_panel(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    window_chrome(draw, (x, y, x + width, y + height), "BarTranslateACO", "Settings")
    sections = [
        ("Provider", [("Translation engine", "Google Translate"), ("Google account", "Sign in   Sign out"), ("Translation history", "Open history")]),
        ("Keyboard Shortcut", [("Toggle app", "⌥  +  ;")]),
        ("Menu Bar", [("Icon style", "Translator bubble")]),
        ("Behavior", [("Auto-paste clipboard", "Off"), ("Launch at login", "Off")]),
        ("About", [("Version", "2.1.5"), ("Updates", "Check for updates")]),
    ]
    yy = y + 92
    for title, rows in sections:
        label(draw, (x + 42, yy), title.upper(), 16, MUTED, True)
        yy += 27
        for row_label, value in rows:
            rounded(draw, (x + 36, yy, x + width - 36, yy + 48), 12, PANEL_2, BORDER, 1)
            label(draw, (x + 58, yy + 13), row_label, 21, TEXT)
            label(draw, (x + width - 58, yy + 13), value, 20, MUTED, anchor="ra")
            yy += 54
        yy += 15


def card(draw: ImageDraw.ImageDraw, y: int, heading: str, body: str) -> None:
    rounded(draw, (1360, y, 2200, y + 142), 24, PANEL_2, BORDER, 1)
    label(draw, (1398, y + 28), heading, 32, TEXT, True)
    label(draw, (1398, y + 82), body, 23, MUTED)


def overview() -> None:
    image = base_image()
    draw = ImageDraw.Draw(image)
    logo(draw, 385, 315, 0.78)
    label(draw, (500, 265), "BarTranslateACO in dark mode", 74, TEXT, True)
    label(draw, (505, 365), "Menu bar translator panel with dark-mode project graphics.", 37, MUTED)
    translate_panel(draw, 350, 520, 900, 660)
    card(draw, 570, "Fork-specific build", "Installs as BarTranslateACO and coexists with upstream BarTranslate.")
    card(draw, 760, "Dark mode first", "Translator pages and README graphics are tuned for dark appearances.")
    card(draw, 950, "Fast translation", "Hotkey access, autofocus, and clipboard support keep translation quick.")
    image.convert("RGB").save(OUT / "bartranslate-dark-overview.png", quality=95)


def settings() -> None:
    image = base_image()
    draw = ImageDraw.Draw(image)
    label(draw, (320, 265), "Settings without sponsor prompts", 74, TEXT, True)
    label(draw, (325, 365), "Native settings panel with fork-specific project information.", 37, MUTED)
    settings_panel(draw, 350, 500, 900, 780)
    card(draw, 570, "README refreshed", "Identifies the fork, thanks the original author, and removes App Store language.")
    card(draw, 760, "Sponsor links removed", "No GitHub Funding metadata or upstream sponsor button remains.")
    card(draw, 950, "Project structure cleaned", "Unused App Store, Electron, and duplicate icon artifacts were removed.")
    image.convert("RGB").save(OUT / "bartranslate-dark-settings.png", quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    overview()
    settings()


if __name__ == "__main__":
    main()
