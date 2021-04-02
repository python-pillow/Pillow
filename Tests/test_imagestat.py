import pytest

from PIL import Image, ImageStat

from .helper import hopper


def test_sanity():

    im = hopper()

    st = ImageStat.Stat(im)
    st = ImageStat.Stat(im.histogram())
    st = ImageStat.Stat(im, Image.new("1", im.size, 1))

    # Check these run. Exceptions will cause failures.
    st.extrema
    st.sum
    st.mean
    st.median
    st.rms
    st.sum2
    st.var
    st.stddev

    with pytest.raises(AttributeError):
        st.spam()

    with pytest.raises(TypeError):
        ImageStat.Stat(1)


def test_hopper():

    im = hopper()

    st = ImageStat.Stat(im)

    # verify a few values
    assert st.extrema[0] == (0, 255)
    assert st.median[0] == 72
    assert st.sum[0] == 1470218
    assert st.sum[1] == 1311896
    assert st.sum[2] == 1563008


def test_constant():

    im = Image.new("L", (128, 128), 128)

    st = ImageStat.Stat(im)

    assert st.extrema[0] == (128, 128)
    assert st.sum[0] == 128 ** 3
    assert st.sum2[0] == 128 ** 4
    assert st.mean[0] == 128
    assert st.median[0] == 128
    assert st.rms[0] == 128
    assert st.var[0] == 0
    assert st.stddev[0] == 0
