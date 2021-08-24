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
        "Tests/images/crash-0c7e0e8e11ce787078f00b5b0ca409a167f070e0.tif",
        "Tests/images/crash-0e16d3bfb83be87356d026d66919deaefca44dac.tif",
        "Tests/images/crash-1152ec2d1a1a71395b6f2ce6721c38924d025bf3.tif",
        "Tests/images/crash-1185209cf7655b5aed8ae5e77784dfdd18ab59e9.tif",
        "Tests/images/crash-338516dbd2f0e83caddb8ce256c22db3bd6dc40f.tif",
        "Tests/images/crash-4f085cc12ece8cde18758d42608bed6a2a2cfb1c.tif",
        "Tests/images/crash-86214e58da443d2b80820cff9677a38a33dcbbca.tif",
        "Tests/images/crash-f46f5b2f43c370fe65706c11449f567ecc345e74.tif",
        "Tests/images/crash-63b1dffefc8c075ddc606c0a2f5fdc15ece78863.tif",
        "Tests/images/crash-74d2a78403a5a59db1fb0a2b8735ac068a75f6e3.tif",
        "Tests/images/crash-81154a65438ba5aaeca73fd502fa4850fbde60f8.tif",
        "Tests/images/crash-0da013a13571cc8eb457a39fee8db18f8a3c7127.tif",
    ],
)
@pytest.mark.filterwarnings("ignore:Possibly corrupt EXIF data")
@pytest.mark.filterwarnings("ignore:Metadata warning")
@pytest.mark.filterwarnings("ignore:Truncated File Read")
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
