"""Frame decoding."""

from __future__ import annotations

import base64
from io import BytesIO

import pytest
from PIL import Image

from utils.images import InvalidFrame, decode_frame, downscale, prepare_frame


def encode(size=(64, 48), fmt="JPEG", mode="RGB") -> str:
    buffer = BytesIO()
    Image.new(mode, size, "red").save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode()


def test_decodes_bare_base64():
    assert decode_frame(encode()).size == (64, 48)


def test_decodes_a_data_url():
    # This is what canvas.toDataURL() hands the extension.
    assert decode_frame(f"data:image/jpeg;base64,{encode()}").size == (64, 48)


def test_converts_transparent_png_to_rgb():
    image = decode_frame(encode(fmt="PNG", mode="RGBA"))
    assert image.mode == "RGB"


@pytest.mark.parametrize("bad", ["", "not base64 at all!!", base64.b64encode(b"nope").decode()])
def test_unusable_input_raises(bad):
    with pytest.raises(InvalidFrame):
        decode_frame(bad)


def test_oversized_payload_is_refused():
    with pytest.raises(InvalidFrame):
        decode_frame(base64.b64encode(b"\x00" * (13 * 1024 * 1024)).decode())


def test_downscale_preserves_aspect_ratio():
    resized = downscale(Image.new("RGB", (4000, 2000)), 1024)
    assert resized.size == (1024, 512)


def test_downscale_leaves_small_frames_alone():
    original = Image.new("RGB", (320, 240))
    assert downscale(original, 1024) is original


def test_downscale_never_produces_a_zero_dimension():
    assert min(downscale(Image.new("RGB", (2000, 3)), 100).size) >= 1


def test_prepare_frame_decodes_and_shrinks():
    assert max(prepare_frame(encode(size=(2048, 1024)), 512).size) == 512
