# Reproductions/tests for crashes/read errors in TiffDecode.c

# When run in Python, all of these images should fail for
# one reason or another, either as a buffer overrun,
# unrecognized datastream, or truncated image file.
# There shouldn't be any segfaults.
#
# if run like
# `valgrind --tool=memcheck pytest test_tiff_crashes.py 2>&1 | grep TiffDecode.c`
# the output should be empty. There may be Python issues
# in the valgrind especially if run in a debug Python
# version.

import pytest

from PIL import Image

from .helper import on_ci


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/crash_1.tif",
        "Tests/images/crash_2.tif",
        "Tests/images/crash-2020-10-test.tif",
        "Tests/images/crash-1152ec2d1a1a71395b6f2ce6721c38924d025bf3.tif",
        "Tests/images/crash-0e16d3bfb83be87356d026d66919deaefca44dac.tif",
    ],
)
@pytest.mark.filterwarnings("ignore:Possibly corrupt EXIF data")
@pytest.mark.filterwarnings("ignore:Metadata warning")
def test_tiff_crashes(test_file):
    try:
        with Image.open(test_file) as im:
            im.load()
    except FileNotFoundError:
        if not on_ci():
            pytest.skip("test image not found")
            return
        raise
    except OSError:
        pass
