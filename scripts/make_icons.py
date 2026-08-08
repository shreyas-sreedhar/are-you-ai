#!/usr/bin/env python3
"""Render the RUAI mark to PNG at every size the extension and docs need.

The mark is pure geometry, so it is drawn here rather than rasterised from
`brand/ruai-mark.svg` — that keeps icon generation dependency-free (Pillow is
already a backend dependency) and reproducible on any machine.

Keep the geometry below in sync with `brand/ruai-mark.svg`.

    python scripts/make_icons.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
EXTENSION_ICONS = ROOT / "extension" / "icons"
BRAND = ROOT / "brand"

# Everything below is expressed on the 128x128 grid used by the SVG.
GRID = 128
SUPERSAMPLE = 8

BRAND_1 = (0x3B, 0x5B, 0xF5)  # indigo
BRAND_2 = (0x8B, 0x3B, 0xF5)  # violet
WHITE = (0xFF, 0xFF, 0xFF)

CORNER_RADIUS = 30
STROKE = 11
HOOK_CENTER = (64, 50)
HOOK_RADIUS = 21
# The hook runs clockwise from its lower-left terminal, over the top, and down
# past 3 o'clock — the extra sweep is what stops it reading as a plain arch.
HOOK_START_DEG = 200
HOOK_END_DEG = 30
TAIL_END = (64, 80)
DOT = (57.5, 91.5, 70.5, 104.5)
DOT_RADIUS = 3.25

# Extension icon sizes (Chrome uses 16 in the toolbar, 128 in the store).
ICON_SIZES = (16, 32, 48, 128)


def _diagonal_gradient(size: int) -> Image.Image:
    """A 135-degree linear gradient, matching the SVG's userSpaceOnUse ramp."""
    ramp = np.linspace(0.0, 1.0, size, dtype=np.float32)
    # Progress along the top-left -> bottom-right diagonal.
    t = ((ramp[None, :] + ramp[:, None]) / 2.0)[..., None]
    start = np.array(BRAND_1, dtype=np.float32)
    end = np.array(BRAND_2, dtype=np.float32)
    pixels = start + (end - start) * t
    return Image.fromarray(pixels.round().astype(np.uint8), mode="RGB")


def _scale(value: float, factor: float) -> float:
    return value * factor


def render_mark(size: int) -> Image.Image:
    """Render the mark at `size` px, drawn large and downsampled for smooth edges."""
    canvas = size * SUPERSAMPLE
    f = canvas / GRID

    # 1. Rounded-square plate filled with the brand gradient.
    plate = Image.new("L", (canvas, canvas), 0)
    ImageDraw.Draw(plate).rounded_rectangle(
        (0, 0, canvas - 1, canvas - 1), radius=_scale(CORNER_RADIUS, f), fill=255
    )
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    image.paste(_diagonal_gradient(canvas), (0, 0), plate)

    draw = ImageDraw.Draw(image)
    stroke = _scale(STROKE, f)
    cap = stroke / 2

    def dot_at(point: tuple[float, float]) -> None:
        """Pillow has no round line caps, so the caps are drawn explicitly."""
        x, y = point[0] * f, point[1] * f
        draw.ellipse((x - cap, y - cap, x + cap, y + cap), fill=WHITE)

    # 2. The question mark's hook.
    cx, cy = HOOK_CENTER
    r = HOOK_RADIUS
    # Overshoot by 2 degrees at each end so the arc tucks under the round caps
    # instead of leaving a hairline notch where they meet.
    draw.arc(
        ((cx - r) * f, (cy - r) * f, (cx + r) * f, (cy + r) * f),
        start=HOOK_START_DEG - 2,
        end=HOOK_END_DEG + 2,
        fill=WHITE,
        width=round(stroke),
    )

    def on_hook(degrees: float) -> tuple[float, float]:
        radians = np.deg2rad(degrees)
        return (cx + r * np.cos(radians), cy + r * np.sin(radians))

    hook_end = on_hook(HOOK_END_DEG)
    dot_at(on_hook(HOOK_START_DEG))
    dot_at(hook_end)

    # 3. The tail, falling from the end of the hook back towards centre.
    draw.line(
        (hook_end[0] * f, hook_end[1] * f, TAIL_END[0] * f, TAIL_END[1] * f),
        fill=WHITE,
        width=round(stroke),
    )
    dot_at(TAIL_END)

    # 4. The dot — a rounded square, not a circle: a pixel, because the
    #    question RUAI asks is always about something on a screen.
    draw.rounded_rectangle(
        tuple(v * f for v in DOT), radius=_scale(DOT_RADIUS, f), fill=WHITE
    )

    return image.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    EXTENSION_ICONS.mkdir(parents=True, exist_ok=True)
    BRAND.mkdir(parents=True, exist_ok=True)

    for size in ICON_SIZES:
        target = EXTENSION_ICONS / f"icon-{size}.png"
        render_mark(size).save(target)
        print(f"wrote {target.relative_to(ROOT)}")

    preview = BRAND / "ruai-mark-512.png"
    render_mark(512).save(preview)
    print(f"wrote {preview.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
