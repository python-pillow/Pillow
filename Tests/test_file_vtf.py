from __future__ import annotations

import pytest

from PIL import Image
from PIL.VtfImagePlugin import (
    VtfPF,
    _closest_power,
    _get_mipmap_count,
    _get_texture_size,
)

from .helper import assert_image_equal, assert_image_similar


@pytest.mark.parametrize(
    ("size", "expected_size"),
    [
        (8, 8),
        (7, 8),
        (9, 8),
        (192, 256),
        (1, 1),
        (2000, 2048),
    ],
)
def test_closest_power(size: int, expected_size: int):
    assert _closest_power(size) == expected_size


@pytest.mark.parametrize(
    ("size", "expected_count"),
    [
        ((1, 1), 1),
        ((2, 2), 2),
        ((4, 4), 3),
        ((8, 8), 4),
        ((128, 128), 8),
        ((256, 256), 9),
        ((512, 512), 10),
        ((1024, 1024), 11),
        ((1024, 1), 11),
    ],
)
def test_get_mipmap_count(size: tuple[int, int], expected_count: int):
    assert _get_mipmap_count(*size) == expected_count


@pytest.mark.parametrize(
    ("pixel_format", "size", "expected_size"),
    [
        (VtfPF.DXT1, (16, 16), (16 * 16) // 2),
        (VtfPF.DXT1_ONEBITALPHA, (16, 16), (16 * 16) // 2),
        (VtfPF.DXT3, (16, 16), 16 * 16),
        (VtfPF.DXT5, (16, 16), 16 * 16),
        (VtfPF.BGR888, (16, 16), 16 * 16 * 3),
        (VtfPF.RGB888, (16, 16), 16 * 16 * 3),
        (VtfPF.RGBA8888, (16, 16), 16 * 16 * 4),
        (VtfPF.UV88, (16, 16), 16 * 16 * 2),
        (VtfPF.A8, (16, 16), 16 * 16),
        (VtfPF.I8, (16, 16), 16 * 16),
        (VtfPF.IA88, (16, 16), 16 * 16 * 2),
    ],
)
def test_get_texture_size(
    pixel_format: VtfPF, size: tuple[int, int], expected_size: int
):
    assert _get_texture_size(pixel_format, *size) == expected_size


@pytest.mark.parametrize(
    ("etalon_path", "file_path", "expected_mode", "epsilon"),
    [
        ("Tests/images/vtf_i8.png", "Tests/images/vtf_i8.vtf", "L", 0.0),
        ("Tests/images/vtf_a8.png", "Tests/images/vtf_a8.vtf", "RGBA", 0.0),
        ("Tests/images/vtf_ia88.png", "Tests/images/vtf_ia88.vtf", "LA", 0.0),
        ("Tests/images/vtf_uv88.png", "Tests/images/vtf_uv88.vtf", "RGB", 0.0),
        ("Tests/images/vtf_rgb888.png", "Tests/images/vtf_rgb888.vtf", "RGB", 0.0),
        ("Tests/images/vtf_bgr888.png", "Tests/images/vtf_bgr888.vtf", "RGB", 0.0),
        ("Tests/images/vtf_dxt1.png", "Tests/images/vtf_dxt1.vtf", "RGBA", 3.0),
        ("Tests/images/vtf_dxt1A.png", "Tests/images/vtf_dxt1A.vtf", "RGBA", 8.0),
        ("Tests/images/vtf_rgba8888.png", "Tests/images/vtf_rgba8888.vtf", "RGBA", 0),
    ],
)
def test_vtf_read(etalon_path: str, file_path: str, expected_mode: str, epsilon: float):
    e = Image.open(etalon_path)
    f = Image.open(file_path)
    assert f.mode == expected_mode
    e = e.convert(expected_mode)
    if epsilon == 0:
        assert_image_equal(e, f)
    else:
        assert_image_similar(e, f, epsilon)


@pytest.mark.parametrize(
    ("pixel_format", "file_path", "expected_mode", "epsilon"),
    [
        (VtfPF.I8, "Tests/images/vtf_i8.png", "L", 0.0),
        (VtfPF.A8, "Tests/images/vtf_a8.png", "RGBA", 0.0),
        (VtfPF.IA88, "Tests/images/vtf_ia88.png", "LA", 0.0),
        (VtfPF.UV88, "Tests/images/vtf_uv88.png", "RGB", 0.0),
        (VtfPF.RGB888, "Tests/images/vtf_rgb888.png", "RGB", 0.0),
        (VtfPF.BGR888, "Tests/images/vtf_bgr888.png", "RGB", 0.0),
        (VtfPF.DXT1, "Tests/images/vtf_dxt1.png", "RGBA", 3.0),
        (VtfPF.DXT1_ONEBITALPHA, "Tests/images/vtf_dxt1A.png", "RGBA", 8.0),
        (VtfPF.RGBA8888, "Tests/images/vtf_rgba8888.png", "RGBA", 0),
    ],
)
def test_vtf_save(
    pixel_format: VtfPF, file_path: str, expected_mode: str, epsilon: float, tmp_path
):
    f: Image.Image = Image.open(file_path)
    out = (tmp_path / "tmp.vtf").as_posix()
    f.save(out, pixel_format=pixel_format)
    if pixel_format == VtfPF.DXT1:
        f = f.convert("RGBA")
    e = Image.open(out)
    assert e.mode == expected_mode
    if epsilon == 0:
        assert_image_equal(e, f)
    else:
        assert_image_similar(e, f, epsilon)
