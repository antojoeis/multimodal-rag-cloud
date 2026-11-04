import io

import pytest
from PIL import Image

from app.image_utils import InvalidImageError, prepare_image


def make_image(size, fmt="JPEG", mode="RGB") -> bytes:
    buf = io.BytesIO()
    Image.new(mode, size, "red").save(buf, format=fmt)
    return buf.getvalue()


def size_of(data: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(data)).size


def test_large_photo_is_shrunk_keeping_aspect_ratio():
    out = prepare_image(make_image((4032, 3024)), max_side=1024)
    assert out.resized
    assert out.original_size == (4032, 3024)
    assert out.sent_size == (1024, 768)
    assert size_of(out.data) == (1024, 768)


def test_small_image_is_passed_through_unchanged():
    data = make_image((640, 480))
    out = prepare_image(data, max_side=1024)
    assert not out.resized
    assert out.data == data


def test_transparent_png_stays_png():
    out = prepare_image(make_image((2000, 1000), fmt="PNG", mode="RGBA"), max_side=1024)
    assert out.data.startswith(b"\x89PNG")
    assert out.sent_size == (1024, 512)


def test_exif_rotation_is_applied():
    img = Image.new("RGB", (400, 200), "red")
    exif = img.getexif()
    exif[0x0112] = 6  # orientation: rotate 90 degrees
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    out = prepare_image(buf.getvalue(), max_side=1024)
    assert out.sent_size == (200, 400)


def test_garbage_bytes_raise():
    with pytest.raises(InvalidImageError):
        prepare_image(b"not really a jpeg", max_side=1024)
