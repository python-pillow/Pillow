from .helper import hopper


def test_palette():
    def palette(mode):
        p = hopper(mode).getpalette()
        if p:
            return p[:10]
        return None

    assert palette("1") is None
    assert palette("L") is None
    assert palette("I") is None
    assert palette("F") is None
    assert palette("P") == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert palette("RGB") is None
    assert palette("RGBA") is None
    assert palette("CMYK") is None
    assert palette("YCbCr") is None
