from tester import *

from PIL import Image

def test_sanity():
    data = lena().tobytes() if py3 else lena().tostring()
    assert_true(isinstance(data, bytes))
