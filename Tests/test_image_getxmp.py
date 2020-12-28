from .helper import hopper


def test_getxmp():
    im = hopper()
    type_repr = repr(type(im.getxmp()))
    assert "dict" in type_repr
