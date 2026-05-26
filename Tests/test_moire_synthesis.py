import pytest
from PIL import Image,ImageOps

def test_moire_output_size():
    img = Image.new("RGB", (100, 100), (128, 128, 128))
    result = ImageOps.moire(img)
    assert result.size == img.size

def test_moire_output_mode():
    img = Image.new("RGB", (100, 100), (128, 128, 128))
    result = ImageOps.moire(img)
    assert result.mode == "RGB"

def test_moire_accepts_non_rgb():
    img = Image.new("L", (100, 100), 128)
    result = ImageOps.moire(img)
    assert result.mode == "RGB"
