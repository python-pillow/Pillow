from PIL import Image


def test_getxmp():
    with Image.open("Tests/images/xmp_test.jpg") as im:
        xmp = im.getxmp()

        assert isinstance(xmp, dict)
        assert isinstance(xmp["Description"][0]["Version"], str)

