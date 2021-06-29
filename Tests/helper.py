"""
Helper functions.
"""

import logging
import os
import shutil
import sys
import sysconfig
import tempfile
from io import BytesIO

import pytest
from packaging.version import parse as parse_version

from PIL import Image, ImageMath, features

logger = logging.getLogger(__name__)


HAS_UPLOADER = False

if os.environ.get("SHOW_ERRORS", None):
    # local img.show for errors.
    HAS_UPLOADER = True

    class test_image_results:
        @staticmethod
        def upload(a, b):
            a.show()
            b.show()


elif "GITHUB_ACTIONS" in os.environ:
    HAS_UPLOADER = True

    class test_image_results:
        @staticmethod
        def upload(a, b):
            dir_errors = os.path.join(os.path.dirname(__file__), "errors")
            os.makedirs(dir_errors, exist_ok=True)
            tmpdir = tempfile.mkdtemp(dir=dir_errors)
            a.save(os.path.join(tmpdir, "a.png"))
            b.save(os.path.join(tmpdir, "b.png"))
            return tmpdir


else:
    try:
        import test_image_results

        HAS_UPLOADER = True
    except ImportError:
        pass


def convert_to_comparable(a, b):
    new_a, new_b = a, b
    if a.mode == "P":
        new_a = Image.new("L", a.size)
        new_b = Image.new("L", b.size)
        new_a.putdata(a.getdata())
        new_b.putdata(b.getdata())
    elif a.mode == "I;16":
        new_a = a.convert("I")
        new_b = b.convert("I")
    return new_a, new_b


def assert_deep_equal(a, b, msg=None):
    try:
        assert len(a) == len(b), msg or f"got length {len(a)}, expected {len(b)}"
    except Exception:
        assert a == b, msg


def assert_image(im, mode, size, msg=None):
    if mode is not None:
        assert im.mode == mode, (
            msg or f"got mode {repr(im.mode)}, expected {repr(mode)}"
        )

    if size is not None:
        assert im.size == size, (
            msg or f"got size {repr(im.size)}, expected {repr(size)}"
        )


def assert_image_equal(a, b, msg=None):
    assert a.mode == b.mode, msg or f"got mode {repr(a.mode)}, expected {repr(b.mode)}"
    assert a.size == b.size, msg or f"got size {repr(a.size)}, expected {repr(b.size)}"
    if a.tobytes() != b.tobytes():
        if HAS_UPLOADER:
            try:
                url = test_image_results.upload(a, b)
                logger.error(f"Url for test images: {url}")
            except Exception:
                pass

        assert False, msg or "got different content"


def assert_image_equal_tofile(a, filename, msg=None, mode=None):
    with Image.open(filename) as img:
        if mode:
            img = img.convert(mode)
        assert_image_equal(a, img, msg)


def assert_image_similar(a, b, epsilon, msg=None):
    assert a.mode == b.mode, msg or f"got mode {repr(a.mode)}, expected {repr(b.mode)}"
    assert a.size == b.size, msg or f"got size {repr(a.size)}, expected {repr(b.size)}"

    a, b = convert_to_comparable(a, b)

    diff = 0
    for ach, bch in zip(a.split(), b.split()):
        chdiff = ImageMath.eval("abs(a - b)", a=ach, b=bch).convert("L")
        diff += sum(i * num for i, num in enumerate(chdiff.histogram()))

    ave_diff = diff / (a.size[0] * a.size[1])
    try:
        assert epsilon >= ave_diff, (
            (msg or "")
            + f" average pixel value difference {ave_diff:.4f} > epsilon {epsilon:.4f}"
        )
    except Exception as e:
        if HAS_UPLOADER:
            try:
                url = test_image_results.upload(a, b)
                logger.error(f"Url for test images: {url}")
            except Exception:
                pass
        raise e


def assert_image_similar_tofile(a, filename, epsilon, msg=None, mode=None):
    with Image.open(filename) as img:
        if mode:
            img = img.convert(mode)
        assert_image_similar(a, img, epsilon, msg)


def assert_all_same(items, msg=None):
    assert items.count(items[0]) == len(items), msg


def assert_not_all_same(items, msg=None):
    assert items.count(items[0]) != len(items), msg


def assert_tuple_approx_equal(actuals, targets, threshold, msg):
    """Tests if actuals has values within threshold from targets"""
    value = True
    for i, target in enumerate(targets):
        value *= target - threshold <= actuals[i] <= target + threshold

    assert value, msg + ": " + repr(actuals) + " != " + repr(targets)


def skip_unless_feature(feature):
    reason = f"{feature} not available"
    return pytest.mark.skipif(not features.check(feature), reason=reason)


def skip_unless_feature_version(feature, version_required, reason=None):
    if not features.check(feature):
        return pytest.mark.skip(f"{feature} not available")
    if reason is None:
        reason = f"{feature} is older than {version_required}"
    version_required = parse_version(version_required)
    version_available = parse_version(features.version(feature))
    return pytest.mark.skipif(version_available < version_required, reason=reason)


def mark_if_feature_version(mark, feature, version_blacklist, reason=None):
    if not features.check(feature):
        return pytest.mark.pil_noop_mark()
    if reason is None:
        reason = f"{feature} is {version_blacklist}"
    version_required = parse_version(version_blacklist)
    version_available = parse_version(features.version(feature))
    if (
        version_available.major == version_required.major
        and version_available.minor == version_required.minor
    ):
        return mark(reason=reason)
    return pytest.mark.pil_noop_mark()


@pytest.mark.skipif(sys.platform.startswith("win32"), reason="Requires Unix or macOS")
class PillowLeakTestCase:
    # requires unix/macOS
    iterations = 100  # count
    mem_limit = 512  # k

    def _get_mem_usage(self):
        """
        Gets the RUSAGE memory usage, returns in K. Encapsulates the difference
        between macOS and Linux rss reporting

        :returns: memory usage in kilobytes
        """

        from resource import RUSAGE_SELF, getrusage

        mem = getrusage(RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            # man 2 getrusage:
            #     ru_maxrss
            # This is the maximum resident set size utilized (in bytes).
            return mem / 1024  # Kb
        else:
            # linux
            # man 2 getrusage
            #        ru_maxrss (since Linux 2.6.32)
            #  This is the maximum resident set size used (in kilobytes).
            return mem  # Kb

    def _test_leak(self, core):
        start_mem = self._get_mem_usage()
        for cycle in range(self.iterations):
            core()
            mem = self._get_mem_usage() - start_mem
            msg = f"memory usage limit exceeded in iteration {cycle}"
            assert mem < self.mem_limit, msg


# helpers


def fromstring(data):
    return Image.open(BytesIO(data))


def tostring(im, string_format, **options):
    out = BytesIO()
    im.save(out, string_format, **options)
    return out.getvalue()


def hopper(mode=None, cache={}):
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


def djpeg_available():
    return bool(shutil.which("djpeg"))


def cjpeg_available():
    return bool(shutil.which("cjpeg"))


def netpbm_available():
    return bool(shutil.which("ppmquant") and shutil.which("ppmtogif"))


def magick_command():
    if sys.platform == "win32":
        magickhome = os.environ.get("MAGICK_HOME", "")
        if magickhome:
            imagemagick = [os.path.join(magickhome, "convert.exe")]
            graphicsmagick = [os.path.join(magickhome, "gm.exe"), "convert"]
        else:
            imagemagick = None
            graphicsmagick = None
    else:
        imagemagick = ["convert"]
        graphicsmagick = ["gm", "convert"]

    if imagemagick and shutil.which(imagemagick[0]):
        return imagemagick
    elif graphicsmagick and shutil.which(graphicsmagick[0]):
        return graphicsmagick


def on_appveyor():
    return "APPVEYOR" in os.environ


def on_github_actions():
    return "GITHUB_ACTIONS" in os.environ


def on_ci():
    # GitHub Actions and AppVeyor have "CI"
    return "CI" in os.environ


def is_big_endian():
    return sys.byteorder == "big"


def is_ppc64le():
    import platform

    return platform.machine() == "ppc64le"


def is_win32():
    return sys.platform.startswith("win32")


def is_pypy():
    return hasattr(sys, "pypy_translation_info")


def is_mingw():
    return sysconfig.get_platform() == "mingw"


class cached_property:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
