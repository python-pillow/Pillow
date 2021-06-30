import pytest

from PIL import Image


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/sgi_overrun_expandrowF04.bin",
        "Tests/images/sgi_crash.bin",
        "Tests/images/crash-6b7f2244da6d0ae297ee0754a424213444e92778.sgi",
        "Tests/images/ossfuzz-5730089102868480.sgi",
        "Tests/images/crash-754d9c7ec485ffb76a90eeaab191ef69a2a3a3cd.sgi",
        "Tests/images/crash-465703f71a0f0094873a3e0e82c9f798161171b8.sgi",
        "Tests/images/crash-64834657ee604b8797bf99eac6a194c124a9a8ba.sgi",
        "Tests/images/crash-abcf1c97b8fe42a6c68f1fb0b978530c98d57ced.sgi",
        "Tests/images/crash-b82e64d4f3f76d7465b6af535283029eda211259.sgi",
        "Tests/images/crash-c1b2595b8b0b92cc5f38b6635e98e3a119ade807.sgi",
        "Tests/images/crash-db8bfa78b19721225425530c5946217720d7df4e.sgi",
    ],
)
def test_crashes(test_file):
    with open(test_file, "rb") as f:
        im = Image.open(f)
        with pytest.raises(OSError):
            im.load()
