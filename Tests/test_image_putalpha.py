from PIL import Image


def test_interface():
    im = Image.new("RGBA", (1, 1), (1, 2, 3, 0))
    assert im.getpixel((0, 0)) == (1, 2, 3, 0)

    im = Image.new("RGBA", (1, 1), (1, 2, 3))
    assert im.getpixel((0, 0)) == (1, 2, 3, 255)

    im.putalpha(Image.new("L", im.size, 4))
    assert im.getpixel((0, 0)) == (1, 2, 3, 4)

    im.putalpha(5)
    assert im.getpixel((0, 0)) == (1, 2, 3, 5)


def test_promote():
    im = Image.new("L", (1, 1), 1)
    assert im.getpixel((0, 0)) == 1

    im.putalpha(2)
    assert im.mode == "LA"
    assert im.getpixel((0, 0)) == (1, 2)

    im = Image.new("P", (1, 1), 1)
    assert im.getpixel((0, 0)) == 1

    im.putalpha(2)
    assert im.mode == "PA"
    assert im.getpixel((0, 0)) == (1, 2)

    im = Image.new("RGB", (1, 1), (1, 2, 3))
    assert im.getpixel((0, 0)) == (1, 2, 3)

    im.putalpha(4)
    assert im.mode == "RGBA"
    assert im.getpixel((0, 0)) == (1, 2, 3, 4)


def test_readonly():
    im = Image.new("RGB", (1, 1), (1, 2, 3))
    im.readonly = 1

    im.putalpha(4)
    assert not im.readonly
    assert im.mode == "RGBA"
    assert im.getpixel((0, 0)) == (1, 2, 3, 4)
