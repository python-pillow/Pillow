"""
Helper functions.
"""
from __future__ import print_function
import sys
import tempfile
import os

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest


class PillowTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        # holds last result object passed to run method:
        self.currentResult = None

    # Nicer output for --verbose
    def __str__(self):
        return self.__class__.__name__ + "." + self._testMethodName

    def run(self, result=None):
        self.currentResult = result  # remember result for use later
        unittest.TestCase.run(self, result)  # call superclass run method

    def delete_tempfile(self, path):
        try:
            ok = self.currentResult.wasSuccessful()
        except AttributeError:  # for nosetests
            proxy = self.currentResult
            ok = (len(proxy.errors) + len(proxy.failures) == 0)

        if ok:
            # only clean out tempfiles if test passed
            try:
                os.remove(path)
            except OSError:
                pass  # report?
        else:
            print("=== orphaned temp file: %s" % path)

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
        if a.tobytes() != b.tobytes():
            self.fail(msg or "got different content")

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
            (msg or '') +
            " average pixel value difference %.4f > epsilon %.4f" % (
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

    def skipKnownBadTest(self, msg=None, platform=None,
                         travis=None, interpreter=None):
        # Skip if platform/travis matches, and
        # PILLOW_RUN_KNOWN_BAD is not true in the environment.
        if bool(os.environ.get('PILLOW_RUN_KNOWN_BAD', False)):
            print(os.environ.get('PILLOW_RUN_KNOWN_BAD', False))
            return

        skip = True
        if platform is not None:
            skip = sys.platform.startswith(platform)
        if travis is not None:
            skip = skip and (travis == bool(os.environ.get('TRAVIS', False)))
        if interpreter is not None:
            skip = skip and (interpreter == 'pypy' and
                             hasattr(sys, 'pypy_version_info'))
        if skip:
            self.skipTest(msg or "Known Bad Test")

    def tempfile(self, template):
        assert template[:5] in ("temp.", "temp_")
        (fd, path) = tempfile.mkstemp(template[4:], template[:4])
        os.close(fd)

        self.addCleanup(self.delete_tempfile, path)
        return path

    def open_withImagemagick(self, f):
        if not imagemagick_available():
            raise IOError()

        outfile = self.tempfile("temp.png")
        if command_succeeds([IMCONVERT, f, outfile]):
            from PIL import Image
            return Image.open(outfile)
        raise IOError()


# helpers

py3 = (sys.version_info >= (3, 0))


def fromstring(data):
    from io import BytesIO
    from PIL import Image
    return Image.open(BytesIO(data))


def tostring(im, string_format, **options):
    from io import BytesIO
    out = BytesIO()
    im.save(out, string_format, **options)
    return out.getvalue()


def hopper(mode=None, cache={}):
    from PIL import Image
    if mode is None:
        # Always return fresh not-yet-loaded version of image.
        # Operations on not-yet-loaded images is separate class of errors
        # what we should catch.
        return Image.open("Tests/images/hopper.ppm")
    # Use caching to reduce reading from disk but so an original copy is
    # returned each time and the cached image isn't modified by tests
    # (for fast, isolated, repeatable tests).
    im = cache.get(mode)
    if im is None:
        if mode == "F":
            im = hopper("L").convert(mode)
        elif mode[:4] == "I;16":
            im = hopper("I").convert(mode)
        else:
            im = hopper().convert(mode)
        cache[mode] = im
    return im.copy()


def command_succeeds(cmd):
    """
    Runs the command, which must be a list of strings. Returns True if the
    command succeeds, or False if an OSError was raised by subprocess.Popen.
    """
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
    return (command_succeeds(["ppmquant", "--help"]) and
            command_succeeds(["ppmtogif", "--help"]))


def imagemagick_available():
    return IMCONVERT and command_succeeds([IMCONVERT, '-version'])


def on_appveyor():
    return 'APPVEYOR' in os.environ

if sys.platform == 'win32':
    IMCONVERT = os.environ.get('MAGICK_HOME', '')
    if IMCONVERT:
        IMCONVERT = os.path.join(IMCONVERT, 'convert.exe')
else:
    IMCONVERT = 'convert'

# End of file
