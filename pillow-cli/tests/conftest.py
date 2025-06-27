"""
Test setup and fixtures for the Pillow CLI project
"""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from PIL import Image, ImageDraw


@pytest.fixture(scope="session")
def test_data_dir():
    """Temp directory that lives for the whole test session"""
    temp_dir = tempfile.mkdtemp(prefix="pillow_cli_test_")
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_test_image():
    """Helper to make test images on demand"""

    def _create_image(
        size=(100, 100), color="red", format="JPEG", mode="RGB", save_path=None
    ):
        image = Image.new(mode, size, color=color)

        # Add some visual elements to make it more realistic
        draw = ImageDraw.Draw(image)
        if size[0] >= 50 and size[1] >= 50:
            # Rectangle in the middle
            rect_size = min(size[0] // 2, size[1] // 2)
            x1, y1 = size[0] // 4, size[1] // 4
            x2, y2 = x1 + rect_size, y1 + rect_size

            if mode == "RGB":
                draw.rectangle([x1, y1, x2, y2], fill="blue")
            elif mode == "RGBA":
                draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 255, 200))

            # Circle around the edge if there's room
            if size[0] >= 20 and size[1] >= 20:
                margin = 5
                draw.ellipse(
                    [margin, margin, size[0] - margin, size[1] - margin],
                    outline="green",
                    width=2,
                )

        if save_path:
            image.save(save_path, format)
            return save_path
        return image

    return _create_image


@pytest.fixture
def sample_images_batch(test_data_dir, create_test_image):
    """Makes a batch of sample images for testing"""
    images = []
    colors = ["red", "green", "blue", "yellow", "purple", "orange"]
    sizes = [(50, 50), (100, 100), (150, 100), (100, 150)]

    for i, (color, size) in enumerate(zip(colors, sizes * 2)):  # cycle through sizes
        if i >= len(colors):
            break
        image_path = os.path.join(test_data_dir, f"batch_image_{i:02d}.jpg")
        create_test_image(size=size, color=color, save_path=image_path)
        images.append(image_path)

    return images


@pytest.fixture
def sample_formats(test_data_dir, create_test_image):
    """Creates test images in different formats for conversion testing"""
    formats_data = {}

    # JPEG
    jpeg_path = os.path.join(test_data_dir, "sample.jpg")
    formats_data["jpeg"] = create_test_image(save_path=jpeg_path, format="JPEG")

    # PNG with transparency
    png_path = os.path.join(test_data_dir, "sample.png")
    formats_data["png"] = create_test_image(
        save_path=png_path, format="PNG", mode="RGBA"
    )

    # BMP
    bmp_path = os.path.join(test_data_dir, "sample.bmp")
    formats_data["bmp"] = create_test_image(save_path=bmp_path, format="BMP")

    # GIF
    gif_path = os.path.join(test_data_dir, "sample.gif")
    formats_data["gif"] = create_test_image(save_path=gif_path, format="GIF")

    return formats_data


def pytest_configure(config):
    """Add our custom test markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "gui: mark test as GUI-related (may require display)"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-assign markers based on test names and classes"""
    for item in items:
        # Unit tests
        if "TestPillowCLI" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Integration tests
        elif "TestIntegration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Slow tests (batch processing, large files, etc.)
        if "batch_process" in item.name or "large_dimensions" in item.name:
            item.add_marker(pytest.mark.slow)

        # GUI tests
        if "gui" in item.name.lower():
            item.add_marker(pytest.mark.gui)
