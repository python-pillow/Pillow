from tester import *
from PIL import Image

import locale

# ref https://github.com/python-imaging/Pillow/issues/272
## on windows, in polish locale:

## import locale
## print locale.setlocale(locale.LC_ALL, 'polish')
## import string
## print len(string.whitespace)
## print ord(string.whitespace[6])

## Polish_Poland.1250
## 7
## 160

# one of string.whitespace is not freely convertable into ascii. 

path = "Images/lena.jpg"

def test_sanity():
    assert_no_exception(lambda: Image.open(path))
    try:
        locale.setlocale(locale.LC_ALL, "polish")
    except:
        skip('polish locale not available')
    import string
    assert_no_exception(lambda: Image.open(path))

