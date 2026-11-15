"""Trim the empty bottom area of headless browser screenshots."""
from pathlib import Path

from PIL import Image

SHOTS = Path(r"D:\SoftwareE\StudyTask\docs\report\shots")
CROPS = {
    "home": 660,
    "filtered": 660,
    "detail": 640,
    "form": 930,
    "delete": 620,
}

for name, bottom in CROPS.items():
    src = SHOTS / f"{name}.png"
    if not src.exists():
        continue
    im = Image.open(src)
    w, h = im.size
    bottom = min(bottom, h)
    im.crop((0, 0, w, bottom)).save(SHOTS / f"{name}-crop.png")
    print(name, w, h, "->", w, bottom)
