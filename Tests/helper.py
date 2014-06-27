"""
Helper functions.
"""
from __future__ import print_function
import sys

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest


# This should be imported into every test_XXX.py file to report
# any remaining temp files at the end of the run.
def tearDownModule():
    import glob
    import os
    import tempfile
    temp_root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
    tempfiles = glob.glob(os.path.join(temp_root, "temp_*"))
    if tempfiles:
        print("===", "remaining temporary files")
        for file in tempfiles:
            print(file)
        print("-"*68)


class PillowTestCase(unittest.TestCase):

    currentResult = None  # holds last result object passed to run method
    _tempfiles = []

    def run(self, result=None):
        self.addCleanup(self.delete_tempfiles)
        self.currentResult = result  # remember result for use later
        unittest.TestCase.run(self, result)  # call superclass run method

    def delete_tempfiles(self):
        try:
            ok = self.currentResult.wasSuccessful()
        except AttributeError:  # for nosetests
            proxy = self.currentResult
            ok = (len(proxy.errors) + len(proxy.failures) == 0)

        if ok:
            # only clean out tempfiles if test passed
            import os
            import os.path
            import tempfile
            for file in self._tempfiles:
                try:
                    os.remove(file)
                except OSError:
                    pass  # report?
            temp_root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
            try:
                os.rmdir(temp_root)
            except OSError:
                pass

    def assert_almost_equal(self, a, b, msg=None, eps=1e-6):
        self.assertLess(
            abs(a-b), eps,
            msg or "got %r, expected %r" % (a, b))

    def assert_deep_equal(self, a, b, msg=None):
        try:
            self.assertEqual(
                len(a), len(b),
                msg or "got length %s, expected %s" % (len(a), len(b)))
            self.assertTrue(
                all([x == y for x, y in zip(a, b)]),
                msg or "got %s, expected %s" % (a, b))
        except:
            self.assertEqual(a, b, msg)

    def assert_image(self, im, mode, size, msg=None):
        if mode is not None:
            self.assertEqual(
                im.mode, mode,
                msg or "got mode %r, expected %r" % (im.mode, mode))

        if size is not None:
            self.assertEqual(
                im.size, size,
                msg or "got size %r, expected %r" % (im.size, size))

    def assert_image_equal(self, a, b, msg=None):
        self.assertEqual(
            a.mode, b.mode,
            msg or "got mode %r, expected %r" % (a.mode, b.mode))
        self.assertEqual(
            a.size, b.size,
            msg or "got size %r, expected %r" % (a.size, b.size))
        self.assertEqual(
            a.tobytes(), b.tobytes(),
            msg or "got different content")

    def assert_image_similar(self, a, b, epsilon, msg=None):
        epsilon = float(epsilon)
        self.assertEqual(
            a.mode, b.mode,
            msg or "got mode %r, expected %r" % (a.mode, b.mode))
        self.assertEqual(
            a.size, b.size,
            msg or "got size %r, expected %r" % (a.size, b.size))

        diff = 0
        try:
            ord(b'0')
            for abyte, bbyte in zip(a.tobytes(), b.tobytes()):
                diff += abs(ord(abyte)-ord(bbyte))
        except:
            for abyte, bbyte in zip(a.tobytes(), b.tobytes()):
                diff += abs(abyte-bbyte)
        ave_diff = float(diff)/(a.size[0]*a.size[1])
        self.assertGreaterEqual(
            epsilon, ave_diff,
            msg or "average pixel value difference %.4f > epsilon %.4f" % (
                ave_diff, epsilon))

    def assert_warning(self, warn_class, func):
        import warnings

        result = None
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            # Hopefully trigger a warning.
            result = func()

            # Verify some things.
            self.assertGreaterEqual(len(w), 1)
            found = False
            for v in w:
                if issubclass(v.category, warn_class):
                    found = True
                    break
            self.assertTrue(found)
        return result

    def tempfile(self, template, *extra):
        import os
        import os.path
        import sys
        import tempfile
        files = []
        root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
        try:
            os.mkdir(root)
        except OSError:
            pass
        for temp in (template,) + extra:
            assert temp[:5] in ("temp.", "temp_")
            name = os.path.basename(sys.argv[0])
            name = temp[:4] + os.path.splitext(name)[0][4:]
            name = name + "_%d" % len(self._tempfiles) + temp[4:]
            name = os.path.join(root, name)
            files.append(name)
        self._tempfiles.extend(files)
        return files[0]


# helpers

import sys
py3 = (sys.version_info >= (3, 0))


def fromstring(data):
    from io import BytesIO
    from PIL import Image
    return Image.open(BytesIO(data))


def tostring(im, format, **options):
    from io import BytesIO
    out = BytesIO()
    im.save(out, format, **options)
    return out.getvalue()


def lena(mode="RGB", cache={}):
    from PIL import Image
    im = None
    # FIXME: Implement caching to reduce reading from disk but so an original
    # copy is returned each time and the cached image isn't modified by tests
    # (for fast, isolated, repeatable tests).
    # im = cache.get(mode)
    if im is None:
        if mode == "RGB":
            im = Image.open("Tests/images/lena.ppm")
        elif mode == "F":
            im = lena("L").convert(mode)
        elif mode[:4] == "I;16":
            im = lena("I").convert(mode)
        else:
            im = lena("RGB").convert(mode)
    # cache[mode] = im
    return im


def command_succeeds(cmd):
    """
    Runs the command, which must be a list of strings. Returns True if the
    command succeeds, or False if an OSError was raised by subprocess.Popen.
    """
    import os
    import subprocess
    with open(os.devnull, 'w') as f:
        try:
            subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT).wait()
        except OSError:
            return False
    return True

def djpeg_available():
    return command_succeeds(['djpeg', '--help'])

def cjpeg_available():
    return command_succeeds(['cjpeg', '--help'])

def netpbm_available():
    return command_succeeds(["ppmquant", "--help"]) and \
           command_succeeds(["ppmtogif", "--help"])

# End of file
