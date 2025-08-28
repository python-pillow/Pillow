from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image

from .helper import assert_image_equal


def test_load_raw() -> None:
    with Image.open("Tests/images/hopper.pcd") as im:
        assert im.size == (768, 512)
        im.load()  # should not segfault.

    # Note that this image was created with a resized hopper
    # image, which was then converted to pcd with imagemagick
    # and the colors are wonky in Pillow.  It's unclear if this
    # is a pillow or a convert issue, as other images not generated
    # from convert look find on pillow and not imagemagick.

    # target = hopper().resize((768,512))
    # assert_image_similar(im, target, 10)


@pytest.mark.parametrize("orientation", (1, 3))
def test_rotated(orientation: int) -> None:
    with open("Tests/images/hopper.pcd", "rb") as fp:
        data = bytearray(fp.read())
    data[2048 + 1538] = orientation
    f = BytesIO(data)
    with Image.open(f) as im:
        assert im.size == (512, 768)

        with Image.open("Tests/images/hopper.pcd") as expected:
            assert_image_equal(
                im, expected.rotate(90 if orientation == 1 else 270, expand=True)
            )
