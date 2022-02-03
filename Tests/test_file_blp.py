import pytest

from PIL import Image

from .helper import assert_image_equal_tofile


def test_load_blp2_raw():
    with Image.open("Tests/images/blp/blp2_raw.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_raw.png")


def test_load_blp2_dxt1():
    with Image.open("Tests/images/blp/blp2_dxt1.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_dxt1.png")


def test_load_blp2_dxt1a():
    with Image.open("Tests/images/blp/blp2_dxt1a.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_dxt1a.png")


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/timeout-060745d3f534ad6e4128c51d336ea5489182c69d.blp",
        "Tests/images/timeout-31c8f86233ea728339c6e586be7af661a09b5b98.blp",
        "Tests/images/timeout-60d8b7c8469d59fc9ffff6b3a3dc0faeae6ea8ee.blp",
        "Tests/images/timeout-8073b430977660cdd48d96f6406ddfd4114e69c7.blp",
        "Tests/images/timeout-bba4f2e026b5786529370e5dfe9a11b1bf991f07.blp",
        "Tests/images/timeout-d6ec061c4afdef39d3edf6da8927240bb07fe9b7.blp",
        "Tests/images/timeout-ef9112a065e7183fa7faa2e18929b03e44ee16bf.blp",
    ],
)
def test_crashes(test_file):
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            with pytest.raises(OSError):
                im.load()
