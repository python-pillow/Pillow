from PIL import Image

TEST_FILE = "Tests/images/fli_overflow.fli"


def test_fli_overflow():

    # this should not crash with a malloc error or access violation
    with Image.open(TEST_FILE) as im:
        im.load()
