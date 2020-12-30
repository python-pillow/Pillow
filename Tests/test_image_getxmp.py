from PIL import Image


def test_getxmp():
    with Image.open("Tests/images/xmp_test.jpg") as im:
        type_repr = repr(type(im.getxmp()))

        assert "dict" in type_repr
        assert isinstance(im.getxmp()["Description"][0]["Version"], str)
