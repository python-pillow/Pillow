from tester import *

from PIL import Image

try:
    from PyQt5.QtGui import QImage, qRgb, qRgba
except:
    try:
        from PyQt4.QtGui import QImage, qRgb, qRgba
    except:
        skip('PyQT4 or 5 not installed')

from PIL import ImageQt

def test_rgb():
    # from https://qt-project.org/doc/qt-4.8/qcolor.html
    # typedef QRgb
    # An ARGB quadruplet on the format #AARRGGBB, equivalent to an unsigned int.

    assert_equal(qRgb(0,0,0), qRgba(0,0,0,255))
    
    def checkrgb(r,g,b):
        val = ImageQt.rgb(r,g,b)
        val = val % 2**24 # drop the alpha
        assert_equal(val >> 16, r)
        assert_equal(((val >> 8 ) % 2**8), g)
        assert_equal(val % 2**8, b)
        
    checkrgb(0,0,0)
    checkrgb(255,0,0)
    checkrgb(0,255,0)
    checkrgb(0,0,255)


def test_image():
    for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
        assert_no_exception(lambda: ImageQt.ImageQt(lena(mode)))
