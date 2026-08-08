"""Frame decoding and downscaling."""

from __future__ import annotations

import base64
import binascii
import logging
from io import BytesIO

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Refuse anything implausible for a video frame before handing it to Pillow.
MAX_DECODED_BYTES = 12 * 1024 * 1024


class InvalidFrame(ValueError):
    """The supplied frame could not be read as an image."""


def decode_frame(encoded: str) -> Image.Image:
    """Decode a base64 frame, with or without a `data:` URL prefix."""
    if not encoded:
        raise InvalidFrame("frame is empty")

    if "," in encoded[:64]:
        encoded = encoded.split(",", 1)[1]

    try:
        raw = base64.b64decode(encoded, validate=False)
    except (binascii.Error, ValueError) as exc:
        raise InvalidFrame("frame is not valid base64") from exc

    if not raw:
        raise InvalidFrame("frame decoded to zero bytes")
    if len(raw) > MAX_DECODED_BYTES:
        raise InvalidFrame("frame is too large")

    try:
        image = Image.open(BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidFrame("frame is not a readable image") from exc

    # JPEG has no alpha, and the models want RGB anyway.
    return image.convert("RGB") if image.mode != "RGB" else image


def downscale(image: Image.Image, max_edge: int) -> Image.Image:
    """Shrink so the longest edge is at most `max_edge`, preserving aspect.

    Frames arrive at up to 4K. Sending them whole costs latency and tokens
    without improving detection — the artefacts that matter survive at 1024px.
    """
    width, height = image.size
    longest = max(width, height)
    if longest <= max_edge:
        return image

    scale = max_edge / longest
    target = (max(1, round(width * scale)), max(1, round(height * scale)))
    logger.debug("downscaling frame %sx%s -> %sx%s", width, height, *target)
    return image.resize(target, Image.Resampling.LANCZOS)


def prepare_frame(encoded: str, max_edge: int) -> Image.Image:
    """Decode and downscale in one step."""
    return downscale(decode_frame(encoded), max_edge)
