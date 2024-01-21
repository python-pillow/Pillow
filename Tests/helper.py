"""
Helper functions.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from io import BytesIO
from typing import Any, Callable, Sequence

import pytest
from packaging.version import parse as parse_version

from PIL import Image, ImageMath, features

logger = logging.getLogger(__name__)

uploader = None
if os.environ.get("SHOW_ERRORS"):
    uploader = "show"
elif "GITHUB_ACTIONS" in os.environ:
    uploader = "github_actions"
else:
    try:
        import test_image_results

        uploader = "aws"
    except ImportError:
        pass


def upload(a: Image.Image, b: Image.Image) -> str | None:
    if uploader == "show":
        # local img.show for errors.
        a.show()
        b.show()
    elif uploader == "github_actions":
        dir_errors = os.path.join(os.path.dirname(__file__), "errors")
        os.makedirs(dir_errors, exist_ok=True)
        tmpdir = tempfile.mkdtemp(dir=dir_errors)
        a.save(os.path.join(tmpdir, "a.png"))
        b.save(os.path.join(tmpdir, "b.png"))
        return tmpdir
    elif uploader == "aws":
        return test_image_results.upload(a, b)
    return None


def convert_to_comparable(
    a: Image.Image, b: Image.Image
) -> tuple[Image.Image, Image.Image]:
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


def assert_deep_equal(
    a: Sequence[Any], b: Sequence[Any], msg: str | None = None
) -> None:
    try:
        assert len(a) == len(b), msg or f"got length {len(a)}, expected {len(b)}"
    except Exception:
        assert a == b, msg


def assert_image(
    im: Image.Image, mode: str, size: tuple[int, int], msg: str | None = None
) -> None:
    if mode is not None:
        assert im.mode == mode, (
            msg or f"got mode {repr(im.mode)}, expected {repr(mode)}"
        )

    if size is not None:
        assert im.size == size, (
            msg or f"got size {repr(im.size)}, expected {repr(size)}"
        )


def assert_image_equal(a: Image.Image, b: Image.Image, msg: str | None = None) -> None:
    assert a.mode == b.mode, msg or f"got mode {repr(a.mode)}, expected {repr(b.mode)}"
    assert a.size == b.size, msg or f"got size {repr(a.size)}, expected {repr(b.size)}"
    if a.tobytes() != b.tobytes():
        try:
            url = upload(a, b)
            if url:
                logger.error("URL for test images: %s", url)
        except Exception:
            pass

        pytest.fail(msg or "got different content")


def assert_image_equal_tofile(
    a: Image.Image, filename: str, msg: str | None = None, mode: str | None = None
) -> None:
    with Image.open(filename) as img:
        if mode:
            img = img.convert(mode)
        assert_image_equal(a, img, msg)


def assert_image_similar(
    a: Image.Image, b: Image.Image, epsilon: float, msg: str | None = None
) -> None:
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
        try:
            url = upload(a, b)
            if url:
                logger.exception("URL for test images: %s", url)
        except Exception:
            pass
        raise e


def assert_image_similar_tofile(
    a: Image.Image,
    filename: str,
    epsilon: float,
    msg: str | None = None,
    mode: str | None = None,
) -> None:
    with Image.open(filename) as img:
        if mode:
            img = img.convert(mode)
        assert_image_similar(a, img, epsilon, msg)


def assert_all_same(items: Sequence[Any], msg: str | None = None) -> None:
    assert items.count(items[0]) == len(items), msg


def assert_not_all_same(items: Sequence[Any], msg: str | None = None) -> None:
    assert items.count(items[0]) != len(items), msg


def assert_tuple_approx_equal(
    actuals: Sequence[int], targets: tuple[int, ...], threshold: int, msg: str
) -> None:
    """Tests if actuals has values within threshold from targets"""
    for i, target in enumerate(targets):
        if not (target - threshold <= actuals[i] <= target + threshold):
            pytest.fail(msg + ": " + repr(actuals) + " != " + repr(targets))


def skip_unless_feature(feature: str) -> pytest.MarkDecorator:
    reason = f"{feature} not available"
    return pytest.mark.skipif(not features.check(feature), reason=reason)


def skip_unless_feature_version(
    feature: str, required: str, reason: str | None = None
) -> pytest.MarkDecorator:
    if not features.check(feature):
        return pytest.mark.skip(f"{feature} not available")
    if reason is None:
        reason = f"{feature} is older than {required}"
    version_required = parse_version(required)
    version_available = parse_version(features.version(feature))
    return pytest.mark.skipif(version_available < version_required, reason=reason)


def mark_if_feature_version(
    mark: pytest.MarkDecorator,
    feature: str,
    version_blacklist: str,
    reason: str | None = None,
) -> pytest.MarkDecorator:
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

    def _get_mem_usage(self) -> float:
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
        # linux
        # man 2 getrusage
        #        ru_maxrss (since Linux 2.6.32)
        #  This is the maximum resident set size used (in kilobytes).
        return mem  # Kb

    def _test_leak(self, core: Callable[[], None]) -> None:
        start_mem = self._get_mem_usage()
        for cycle in range(self.iterations):
            core()
            mem = self._get_mem_usage() - start_mem
            msg = f"memory usage limit exceeded in iteration {cycle}"
            assert mem < self.mem_limit, msg


# helpers


def fromstring(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data))


def tostring(im: Image.Image, string_format: str, **options: dict[str, Any]) -> bytes:
    out = BytesIO()
    im.save(out, string_format, **options)
    return out.getvalue()


def hopper(mode: str | None = None, cache: dict[str, Image.Image] = {}) -> Image.Image:
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


def djpeg_available() -> bool:
    if shutil.which("djpeg"):
        try:
            subprocess.check_call(["djpeg", "-version"])
            return True
        except subprocess.CalledProcessError:  # pragma: no cover
            return False
    return False


def cjpeg_available() -> bool:
    if shutil.which("cjpeg"):
        try:
            subprocess.check_call(["cjpeg", "-version"])
            return True
        except subprocess.CalledProcessError:  # pragma: no cover
            return False
    return False


def netpbm_available() -> bool:
    return bool(shutil.which("ppmquant") and shutil.which("ppmtogif"))


def magick_command() -> list[str] | None:
    if sys.platform == "win32":
        magickhome = os.environ.get("MAGICK_HOME")
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
    if graphicsmagick and shutil.which(graphicsmagick[0]):
        return graphicsmagick
    return None


def on_appveyor() -> bool:
    return "APPVEYOR" in os.environ


def on_github_actions() -> bool:
    return "GITHUB_ACTIONS" in os.environ


def on_ci() -> bool:
    # GitHub Actions and AppVeyor have "CI"
    return "CI" in os.environ


def is_big_endian() -> bool:
    return sys.byteorder == "big"


def is_ppc64le() -> bool:
    import platform

    return platform.machine() == "ppc64le"


def is_win32() -> bool:
    return sys.platform.startswith("win32")


def is_pypy() -> bool:
    return hasattr(sys, "pypy_translation_info")


def is_mingw() -> bool:
    return sysconfig.get_platform() == "mingw"


class CachedProperty:
    def __init__(self, func: Callable[[Any], None]) -> None:
        self.func = func

    def __get__(self, instance: Any, cls: type[Any] | None = None) -> Any:
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
