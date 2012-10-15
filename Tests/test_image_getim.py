from tester import *

from PIL import Image

def test_sanity():

    im = lena()
    type_repr = repr(type(im.getim()))

    if py3:
        assert_true("PyCapsule" in type_repr)

    assert_true(isinstance(im.im.id, int))

