from tester import *

from PIL import Image

def test_sanity():
    data = lena().tobytes()
    assert_true(isinstance(data, bytes))
