from __future__ import annotations

import pytest
from PIL import Image

from .helper import assert_image_equal, assert_image_similar, hopper

@pytest.fixture
def result():
    return hopper("P").convert("RGB")

@pytest.fixture
def target():
    return hopper("RGB")

def test_upload_equal(result, target):
    assert_image_equal(result, target)

def test_upload_similar(result, target, epsilon):
    assert_image_similar(result, target, epsilon)

@pytest.mark.parametrize("epsilon", [0, 1, 100])
def test_upload_similar_parametrized(result, target, epsilon):
    assert_image_similar(result, target, epsilon)

def test_upload_equal_different_formats():
    result = Image.open("Tests/images/hopper_webp.png").convert("RGB")
    target = Image.open("Tests/images/hopper_webp.tif").convert("RGB")
    assert_image_equal(result, target)

def test_upload_equal_different_sizes():
    result = hopper("P").resize((100, 100)).convert("RGB")
    target = hopper("RGB").resize((200, 200))
    assert_image_equal(result, target)

def test_upload_not_similar():
    result = hopper("P").convert("RGB")
    target = Image.new("RGB", (100, 100), "white")
    with pytest.raises(AssertionError):
        assert_image_similar(result, target, 0)

def test_upload_equal_different_modes():
    result = hopper("L").convert("RGB")
    target = hopper("1").convert("RGB")
    assert_image_equal(result, target)
    