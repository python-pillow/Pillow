import pytest

from PIL import Image

def test_merge_wrong_number_of_bands():
    R = Image.new('L', (100, 100), color=255)
    G = Image.new('L', (100, 100), color=128)
    with pytest.raises(ValueError, match="wrong number of bands"):
        Image.merge('RGB', [R, G]) 

def test_merge_mode_mismatch():
    R = Image.new('L', (100, 100), color=255)
    G = Image.new('L', (100, 100), color=128)
    B = Image.new('1', (100, 100))  # Incorrect mode
    with pytest.raises(ValueError, match="mode mismatch"):
        Image.merge('RGB', [R, G, B])

def test_merge_size_mismatch():
    R = Image.new('L', (100, 100), color=255)
    G = Image.new('L', (200, 100), color=128)  # Different size
    B = Image.new('L', (100, 100), color=0)
    with pytest.raises(ValueError, match="size mismatch"):
        Image.merge('RGB', [R, G, B])

        
