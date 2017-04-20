from helper import unittest, PillowTestCase, hopper, on_appveyor

try:
    from PIL import PyAccess
except ImportError:
    # Skip in setUp()
    pass

from PIL import Image
import sys
import os

class AccessTest(PillowTestCase):
    # initial value
    _init_cffi_access = Image.USE_CFFI_ACCESS
    _need_cffi_access = False

    @classmethod
    def setUpClass(cls):
        Image.USE_CFFI_ACCESS = cls._need_cffi_access

    @classmethod
    def tearDownClass(cls):
        Image.USE_CFFI_ACCESS = cls._init_cffi_access


class TestImagePutPixel(AccessTest):
    def test_sanity(self):
        im1 = hopper()
        im2 = Image.new(im1.mode, im1.size, 0)

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                im2.putpixel(pos, im1.getpixel(pos))

        self.assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)
        im2.readonly = 1

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                im2.putpixel(pos, im1.getpixel(pos))

        self.assertFalse(im2.readonly)
        self.assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)

        pix1 = im1.load()
        pix2 = im2.load()

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pix2[x, y] = pix1[x, y]

        self.assert_image_equal(im1, im2)


class TestImageGetPixel(AccessTest):
    @staticmethod
    def color(mode):
        bands = Image.getmodebands(mode)
        if bands == 1:
            return 1
        else:
            return tuple(range(1, bands + 1))

    def check(self, mode, c=None):
        if not c:
            c = self.color(mode)

        # check putpixel
        im = Image.new(mode, (1, 1), None)
        im.putpixel((0, 0), c)
        self.assertEqual(
            im.getpixel((0, 0)), c,
            "put/getpixel roundtrip failed for mode %s, color %s" % (mode, c))

        # Check 0
        im = Image.new(mode, (0, 0), None)
        with self.assertRaises(IndexError):
            im.putpixel((0, 0), c)
        with self.assertRaises(IndexError):
            im.getpixel((0, 0))

        # check initial color
        im = Image.new(mode, (1, 1), c)
        self.assertEqual(
            im.getpixel((0, 0)), c,
            "initial color failed for mode %s, color %s " % (mode, c))

        # Check 0
        im = Image.new(mode, (0, 0), c)
        with self.assertRaises(IndexError):
            im.getpixel((0, 0))

    def test_basic(self):
        for mode in ("1", "L", "LA", "I", "I;16", "I;16B", "F",
                     "P", "PA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"):
            self.check(mode)

    def test_signedness(self):
        # see https://github.com/python-pillow/Pillow/issues/452
        # pixelaccess is using signed int* instead of uint*
        for mode in ("I;16", "I;16B"):
            self.check(mode, 2**15-1)
            self.check(mode, 2**15)
            self.check(mode, 2**15+1)
            self.check(mode, 2**16-1)


class TestCffiPutPixel(TestImagePutPixel):
    _need_cffi_access = True

    def setUp(self):
        try:
            import cffi
            assert cffi  # silence warning
        except ImportError:
            self.skipTest("No cffi")


class TestCffiGetPixel(TestImageGetPixel):
    _need_cffi_access = True

    def setUp(self):
        try:
            import cffi
            assert cffi  # silence warning
        except ImportError:
            self.skipTest("No cffi")


class TestCffi(AccessTest):
    _need_cffi_access = True

    def setUp(self):
        try:
            import cffi
            assert cffi  # silence warning
        except ImportError:
            self.skipTest("No cffi")

    def _test_get_access(self, im):
        """Do we get the same thing as the old pixel access

        Using private interfaces, forcing a capi access and
        a pyaccess for the same image"""
        caccess = im.im.pixel_access(False)
        access = PyAccess.new(im, False)

        w, h = im.size
        for x in range(0, w, 10):
            for y in range(0, h, 10):
                self.assertEqual(access[(x, y)], caccess[(x, y)])

        # Access an out-of-range pixel
        self.assertRaises(ValueError,
                          lambda: access[(access.xsize+1, access.ysize+1)])

    def test_get_vs_c(self):
        rgb = hopper('RGB')
        rgb.load()
        self._test_get_access(rgb)
        self._test_get_access(hopper('RGBA'))
        self._test_get_access(hopper('L'))
        self._test_get_access(hopper('LA'))
        self._test_get_access(hopper('1'))
        self._test_get_access(hopper('P'))
        # self._test_get_access(hopper('PA')) # PA -- how do I make a PA image?
        self._test_get_access(hopper('F'))

        im = Image.new('I;16', (10, 10), 40000)
        self._test_get_access(im)
        im = Image.new('I;16L', (10, 10), 40000)
        self._test_get_access(im)
        im = Image.new('I;16B', (10, 10), 40000)
        self._test_get_access(im)

        im = Image.new('I', (10, 10), 40000)
        self._test_get_access(im)
        # These don't actually appear to be modes that I can actually make,
        # as unpack sets them directly into the I mode.
        # im = Image.new('I;32L', (10, 10), -2**10)
        # self._test_get_access(im)
        # im = Image.new('I;32B', (10, 10), 2**10)
        # self._test_get_access(im)

    def _test_set_access(self, im, color):
        """Are we writing the correct bits into the image?

        Using private interfaces, forcing a capi access and
        a pyaccess for the same image"""
        caccess = im.im.pixel_access(False)
        access = PyAccess.new(im, False)

        w, h = im.size
        for x in range(0, w, 10):
            for y in range(0, h, 10):
                access[(x, y)] = color
                self.assertEqual(color, caccess[(x, y)])

        # Attempt to set the value on a read-only image
        access = PyAccess.new(im, True)
        with self.assertRaises(ValueError):
            access[(0, 0)] = color

    def test_set_vs_c(self):
        rgb = hopper('RGB')
        rgb.load()
        self._test_set_access(rgb, (255, 128, 0))
        self._test_set_access(hopper('RGBA'), (255, 192, 128, 0))
        self._test_set_access(hopper('L'), 128)
        self._test_set_access(hopper('LA'), (128, 128))
        self._test_set_access(hopper('1'), 255)
        self._test_set_access(hopper('P'), 128)
        # self._test_set_access(i, (128, 128))  #PA  -- undone how to make
        self._test_set_access(hopper('F'), 1024.0)

        im = Image.new('I;16', (10, 10), 40000)
        self._test_set_access(im, 45000)
        im = Image.new('I;16L', (10, 10), 40000)
        self._test_set_access(im, 45000)
        im = Image.new('I;16B', (10, 10), 40000)
        self._test_set_access(im, 45000)

        im = Image.new('I', (10, 10), 40000)
        self._test_set_access(im, 45000)
        # im = Image.new('I;32L', (10, 10), -(2**10))
        # self._test_set_access(im, -(2**13)+1)
        # im = Image.new('I;32B', (10, 10), 2**10)
        # self._test_set_access(im, 2**13-1)

    def test_not_implemented(self):
        self.assertIsNone(PyAccess.new(hopper("BGR;15")))

    # ref https://github.com/python-pillow/Pillow/pull/2009
    def test_reference_counting(self):
        size = 10

        for _ in range(10):
            # Do not save references to the image, only to the access object
            px = Image.new('L', (size, 1), 0).load()
            for i in range(size):
                # pixels can contain garbage if image is released
                self.assertEqual(px[i, 0], 0)


class TestEmbeddable(unittest.TestCase):
    @unittest.skipIf(not sys.platform.startswith('win32') or
                     sys.version_info[:2] in ((3, 3), (3, 4)) or
                     on_appveyor(),   # failing on appveyor when run from
                                      # subprocess, not from shell
                     "requires Python 2.7 or >=3.5 for Windows")
    def test_embeddable(self):
        import subprocess
        import ctypes
        import setuptools
        from distutils import ccompiler, sysconfig

        with open('embed_pil.c', 'w') as fh:
            fh.write("""
#include "Python.h"

int main(int argc, char* argv[])
{
    char *home = "%s";
#if PY_MAJOR_VERSION >= 3
    wchar_t *whome = Py_DecodeLocale(home, NULL);
    Py_SetPythonHome(whome);
#else
    Py_SetPythonHome(home);
#endif

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

#if PY_MAJOR_VERSION >= 3
    PyMem_RawFree(whome);
#endif

    return 0;
}
        """ % sys.prefix.replace('\\', '\\\\'))

        compiler = ccompiler.new_compiler()
        compiler.add_include_dir(sysconfig.get_python_inc())
        
        libdir = sysconfig.get_config_var('LIBDIR') or sysconfig.get_python_inc().replace('include', 'libs')
        print (libdir)
        compiler.add_library_dir(libdir)
        objects = compiler.compile(['embed_pil.c'])
        compiler.link_executable(objects, 'embed_pil')

        env = os.environ.copy()
        env["PATH"] = sys.prefix + ';' + env["PATH"]
        
        # do not display the Windows Error Reporting dialog
        ctypes.windll.kernel32.SetErrorMode(0x0002)
        
        process = subprocess.Popen(['embed_pil.exe'], env=env)
        process.communicate()
        self.assertEqual(process.returncode, 0)

if __name__ == '__main__':
    unittest.main()
