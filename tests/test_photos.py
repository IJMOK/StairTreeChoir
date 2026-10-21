"""Photos in the repo must not carry GPS data (phones embed the home's location)."""

from pathlib import Path

from PIL import Image

PHOTOS = Path(__file__).resolve().parents[1] / "photos"


def test_no_gps_in_photos():
    with_gps = [p.name for p in sorted(PHOTOS.glob("*")) if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".heic")
                and Image.open(p).getexif().get_ifd(0x8825)]
    assert not with_gps, f"strip GPS before committing (see photos/README.md): {with_gps}"
