from tester import *

from PIL import Image
from PIL import ImageStat

def test_sanity():

    im = lena()

    st = ImageStat.Stat(im)
    st = ImageStat.Stat(im.histogram())
    st = ImageStat.Stat(im, Image.new("1", im.size, 1))

    assert_no_exception(lambda: st.extrema)
    assert_no_exception(lambda: st.sum)
    assert_no_exception(lambda: st.mean)
    assert_no_exception(lambda: st.median)
    assert_no_exception(lambda: st.rms)
    assert_no_exception(lambda: st.sum2)
    assert_no_exception(lambda: st.var)
    assert_no_exception(lambda: st.stddev)
    assert_exception(AttributeError, lambda: st.spam)

    assert_exception(TypeError, lambda: ImageStat.Stat(1))

def test_lena():

    im = lena()

    st = ImageStat.Stat(im)

    # verify a few values
    assert_equal(st.extrema[0], (61, 255))
    assert_equal(st.median[0], 197)
    assert_equal(st.sum[0], 2954416)
    assert_equal(st.sum[1], 2027250)
    assert_equal(st.sum[2], 1727331)

def test_constant():

    im = Image.new("L", (128, 128), 128)

    st = ImageStat.Stat(im)

    assert_equal(st.extrema[0], (128, 128))
    assert_equal(st.sum[0], 128**3)
    assert_equal(st.sum2[0], 128**4)
    assert_equal(st.mean[0], 128)
    assert_equal(st.median[0], 128)
    assert_equal(st.rms[0], 128)
    assert_equal(st.var[0], 0)
    assert_equal(st.stddev[0], 0)
