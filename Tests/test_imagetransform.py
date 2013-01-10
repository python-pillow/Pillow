from tester import *

from PIL import Image
from PIL import ImageTransform

im = Image.new("L", (100, 100))

seq = tuple(range(10))

def test_sanity():
    transform = ImageTransform.AffineTransform(seq[:6])
    assert_no_exception(lambda: im.transform((100, 100), transform))
    transform = ImageTransform.ExtentTransform(seq[:4])
    assert_no_exception(lambda: im.transform((100, 100), transform))
    transform = ImageTransform.QuadTransform(seq[:8])
    assert_no_exception(lambda: im.transform((100, 100), transform))
    transform = ImageTransform.MeshTransform([(seq[:4], seq[:8])])
    assert_no_exception(lambda: im.transform((100, 100), transform))
