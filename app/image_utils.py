"""Shrink uploaded images before they reach the vision model.

Qwen2.5-VL turns roughly every 28x28 pixel patch into one token, so a full
phone photo (~4000x3000) becomes ~4000 tokens and overflows a 4096-token
context window. The prompt then gets truncated and the model returns garbage.
"""
import io
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError


class InvalidImageError(ValueError):
    pass


@dataclass
class PreparedImage:
    data: bytes
    original_size: tuple[int, int]
    sent_size: tuple[int, int]

    @property
    def resized(self) -> bool:
        return self.original_size != self.sent_size


def prepare_image(data: bytes, max_side: int) -> PreparedImage:
    """Fix EXIF rotation and shrink so the longest side is at most max_side."""
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("File is not a readable image") from exc

    original = img.size
    img = ImageOps.exif_transpose(img)  # phone photos are often stored sideways
    if max(img.size) <= max_side and img.size == original:
        return PreparedImage(data, original, original)

    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P"):
        img.save(buf, format="PNG")
    else:
        img.convert("RGB").save(buf, format="JPEG", quality=90)
    return PreparedImage(buf.getvalue(), original, img.size)
