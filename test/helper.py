"""
Helper functions.
"""
from __future__ import print_function
import sys

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest


class PillowTestCase(unittest.TestCase):

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

# # require that deprecation warnings are triggered
# import warnings
# warnings.simplefilter('default')
# # temporarily turn off resource warnings that warn about unclosed
# # files in the test scripts.
# try:
#     warnings.filterwarnings("ignore", category=ResourceWarning)
# except NameError:
#     # we expect a NameError on py2.x, since it doesn't have ResourceWarnings.
#     pass

import sys
py3 = (sys.version_info >= (3, 0))

# # some test helpers
#
# _target = None
# _tempfiles = []
# _logfile = None
#
#
# def success():
#     import sys
#     success.count += 1
#     if _logfile:
#         print(sys.argv[0], success.count, failure.count, file=_logfile)
#     return True
#
#
# def failure(msg=None, frame=None):
#     import sys
#     import linecache
#     failure.count += 1
#     if _target:
#         if frame is None:
#             frame = sys._getframe()
#             while frame.f_globals.get("__name__") != _target.__name__:
#                 frame = frame.f_back
#         location = (frame.f_code.co_filename, frame.f_lineno)
#         prefix = "%s:%d: " % location
#         line = linecache.getline(*location)
#         print(prefix + line.strip() + " failed:")
#     if msg:
#         print("- " + msg)
#     if _logfile:
#         print(sys.argv[0], success.count, failure.count, file=_logfile)
#     return False
#
# success.count = failure.count = 0
#
#
# # predicates
#
# def assert_almost_equal(a, b, msg=None, eps=1e-6):
#     if abs(a-b) < eps:
#         success()
#     else:
#         failure(msg or "got %r, expected %r" % (a, b))
#
#
# def assert_deep_equal(a, b, msg=None):
#     try:
#         if len(a) == len(b):
#             if all([x == y for x, y in zip(a, b)]):
#                 success()
#             else:
#                 failure(msg or "got %s, expected %s" % (a, b))
#         else:
#             failure(msg or "got length %s, expected %s" % (len(a), len(b)))
#     except:
#         assert_equal(a, b, msg)
#
#
# def assert_match(v, pattern, msg=None):
#     import re
#     if re.match(pattern, v):
#         success()
#     else:
#         failure(msg or "got %r, doesn't match pattern %r" % (v, pattern))


# helpers

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
    # im = cache.get(mode)
    if im is None:
        if mode == "RGB":
            im = Image.open("Images/lena.ppm")
        elif mode == "F":
            im = lena("L").convert(mode)
        elif mode[:4] == "I;16":
            im = lena("I").convert(mode)
        else:
            im = lena("RGB").convert(mode)
    # cache[mode] = im
    return im


# def assert_image_completely_equal(a, b, msg=None):
#     if a != b:
#         failure(msg or "images different")
#     else:
#         success()
#
#
# def tempfile(template, *extra):
#     import os
#     import os.path
#     import sys
#     import tempfile
#     files = []
#     root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
#     try:
#         os.mkdir(root)
#     except OSError:
#         pass
#     for temp in (template,) + extra:
#         assert temp[:5] in ("temp.", "temp_")
#         name = os.path.basename(sys.argv[0])
#         name = temp[:4] + os.path.splitext(name)[0][4:]
#         name = name + "_%d" % len(_tempfiles) + temp[4:]
#         name = os.path.join(root, name)
#         files.append(name)
#     _tempfiles.extend(files)
#     return files[0]
#
#
# # test runner
#
# def run():
#     global _target, _tests, run
#     import sys
#     import traceback
#     _target = sys.modules["__main__"]
#     run = None  # no need to run twice
#     tests = []
#     for name, value in list(vars(_target).items()):
#         if name[:5] == "test_" and type(value) is type(success):
#             tests.append((value.__code__.co_firstlineno, name, value))
#     tests.sort()  # sort by line
#     for lineno, name, func in tests:
#         try:
#             _tests = []
#             func()
#             for func, args in _tests:
#                 func(*args)
#         except:
#             t, v, tb = sys.exc_info()
#             tb = tb.tb_next
#             if tb:
#                 failure(frame=tb.tb_frame)
#                 traceback.print_exception(t, v, tb)
#             else:
#                 print("%s:%d: cannot call test function: %s" % (
#                     sys.argv[0], lineno, v))
#                 failure.count += 1
#
#
# def yield_test(function, *args):
#     # collect delayed/generated tests
#     _tests.append((function, args))
#
#
# def skip(msg=None):
#     import os
#     print("skip")
#     os._exit(0)  # don't run exit handlers
#
#
# def ignore(pattern):
#     """Tells the driver to ignore messages matching the pattern, for the
#     duration of the current test."""
#     print('ignore: %s' % pattern)
#
#
# def _setup():
#     global _logfile
#
#     import sys
#     if "--coverage" in sys.argv:
#         # Temporary: ignore PendingDeprecationWarning from Coverage (Py3.4)
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             import coverage
#         cov = coverage.coverage(auto_data=True, include="PIL/*")
#         cov.start()
#
#     def report():
#         if run:
#             run()
#         if success.count and not failure.count:
#             print("ok")
#             # only clean out tempfiles if test passed
#             import os
#             import os.path
#             import tempfile
#             for file in _tempfiles:
#                 try:
#                     os.remove(file)
#                 except OSError:
#                     pass  # report?
#             temp_root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
#             try:
#                 os.rmdir(temp_root)
#             except OSError:
#                 pass
#
#     import atexit
#     atexit.register(report)
#
#     if "--log" in sys.argv:
#         _logfile = open("test.log", "a")
#
#
# _setup()
