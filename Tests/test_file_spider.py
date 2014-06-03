from tester import *

from PIL import Image
from PIL import SpiderImagePlugin

test_file = "Tests/images/lena.spider"


def test_sanity():
    im = Image.open(test_file)
    im.load()
    assert_equal(im.mode, "F")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "SPIDER")


def test_save():
    # Arrange
    temp = tempfile('temp.spider')
    im = lena()

    # Act
    im.save(temp, "SPIDER")

    # Assert
    im2 = Image.open(temp)
    assert_equal(im2.mode, "F")
    assert_equal(im2.size, (128, 128))
    assert_equal(im2.format, "SPIDER")


def test_isSpiderImage():
    assert_true(SpiderImagePlugin.isSpiderImage(test_file))


# End of file
