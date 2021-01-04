from .helper import hopper


def test_entropy():
    def entropy(mode):
        return hopper(mode).entropy()

    assert round(abs(entropy("1") - 0.9138803254693582), 7) == 0
    assert round(abs(entropy("L") - 7.063008716585465), 7) == 0
    assert round(abs(entropy("I") - 7.063008716585465), 7) == 0
    assert round(abs(entropy("F") - 7.063008716585465), 7) == 0
    assert round(abs(entropy("P") - 5.0530452472519745), 7) == 0
    assert round(abs(entropy("RGB") - 8.821286587714319), 7) == 0
    assert round(abs(entropy("RGBA") - 7.42724306524488), 7) == 0
    assert round(abs(entropy("CMYK") - 7.4272430652448795), 7) == 0
    assert round(abs(entropy("YCbCr") - 7.698360534903628), 7) == 0
