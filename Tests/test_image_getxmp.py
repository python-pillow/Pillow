from PIL import Image


def test_getxmp():
    im = Image.open("Tests/images/hopper.jpg")
    type_repr = repr(type(im.getxmp()))


    assert "dict" in type_repr
