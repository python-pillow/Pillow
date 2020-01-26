from PIL import Image


def test_white():
    with Image.open("Tests/images/lab.tif") as i:
        i.load()

        assert i.mode == "LAB"

        assert i.getbands() == ("L", "A", "B")

        k = i.getpixel((0, 0))

        L = i.getdata(0)
        a = i.getdata(1)
        b = i.getdata(2)

    assert k == (255, 128, 128)

    assert list(L) == [255] * 100
    assert list(a) == [128] * 100
    assert list(b) == [128] * 100


def test_green():
    # l= 50 (/100), a = -100 (-128 .. 128) b=0 in PS
    # == RGB: 0, 152, 117
    with Image.open("Tests/images/lab-green.tif") as i:
        k = i.getpixel((0, 0))
    assert k == (128, 28, 128)


def test_red():
    # l= 50 (/100), a = 100 (-128 .. 128) b=0 in PS
    # == RGB: 255, 0, 124
    with Image.open("Tests/images/lab-red.tif") as i:
        k = i.getpixel((0, 0))
    assert k == (128, 228, 128)
