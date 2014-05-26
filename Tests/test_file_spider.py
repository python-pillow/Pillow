from tester import *

from PIL import Image

test_file = "Tests/images/lena.spider"


def test_sanity():
    im = Image.open(test_file)
    im.load()
    assert_equal(im.mode, "F")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "SPIDER")

# End of file
