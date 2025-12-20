from __future__ import annotations

import io

from PIL import Image, ImageDraw


def test_tiff_palette() -> None:
    image = Image.new("P", (3, 1))
    file = io.BytesIO()
    image.save(file, "tiff")

    image = Image.open(file)
    draw = ImageDraw.Draw(image)
    COLOR_0 = (1, 2, 3)
    COLOR_1 = (127, 128, 129)
    COLOR_2 = (252, 253, 254)
    draw.point((0, 0), fill=COLOR_0)
    draw.point((1, 0), fill=COLOR_1)
    draw.point((2, 0), fill=COLOR_2)

    converted_data = list(image.convert("RGB").getdata())
    assert len(converted_data) == 3
    assert converted_data[0] == COLOR_0
    assert converted_data[1] == COLOR_1
    assert converted_data[2] == COLOR_2
