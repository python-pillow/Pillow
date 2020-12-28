from .helper import hopper

def test_getxmp():
    im = hopper()
    assert type(im.getxmp()) == dict
