from PIL import Image

from .helper import hopper


def test_sanity():
    im = hopper()

    projection = im.getprojection()

    assert len(projection) == 2
    assert len(projection[0]) == im.size[0]
    assert len(projection[1]) == im.size[1]

    # 8-bit image
    im = Image.new("L", (10, 10))
    assert im.getprojection()[0] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert im.getprojection()[1] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    im.paste(255, (2, 4, 8, 6))
    assert im.getprojection()[0] == [0, 0, 1, 1, 1, 1, 1, 1, 0, 0]
    assert im.getprojection()[1] == [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]

    # 32-bit image
    im = Image.new("RGB", (10, 10))
    assert im.getprojection()[0] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert im.getprojection()[1] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    im.paste(255, (2, 4, 8, 6))
    assert im.getprojection()[0] == [0, 0, 1, 1, 1, 1, 1, 1, 0, 0]
    assert im.getprojection()[1] == [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
