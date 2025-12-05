from __future__ import annotations

from PIL import Image, ImageChops


def test_compare_identical_images():
    im1 = Image.new("RGB", (10, 10), "red")
    im2 = Image.new("RGB", (10, 10), "red")

    result = ImageChops.compare_images(im1, im2)

    assert result["different_pixels"] == 0
    assert result["percent_difference"] == 0.0


def test_compare_different_images():
    im1 = Image.new("RGB", (10, 10), "red")
    im2 = Image.new("RGB", (10, 10), "blue")

    result = ImageChops.compare_images(im1, im2)

    assert result["different_pixels"] > 0
    assert result["percent_difference"] > 0.0
