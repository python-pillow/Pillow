import locale
import unittest

from PIL import Image

from .helper import PillowTestCase

# ref https://github.com/python-pillow/Pillow/issues/272
# on windows, in polish locale:

# import locale
# print(locale.setlocale(locale.LC_ALL, 'polish'))
# import string
# print(len(string.whitespace))
# print(ord(string.whitespace[6]))

# Polish_Poland.1250
# 7
# 160

# one of string.whitespace is not freely convertable into ascii.

path = "Tests/images/hopper.jpg"


class TestLocale(PillowTestCase):
    def test_sanity(self):
        with Image.open(path):
            pass
        try:
            locale.setlocale(locale.LC_ALL, "polish")
        except locale.Error:
            unittest.skip("Polish locale not available")

        try:
            with Image.open(path):
                pass
        finally:
            locale.setlocale(locale.LC_ALL, (None, None))
