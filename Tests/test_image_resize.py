"""
Tests for resize functionality.
"""
from itertools import permutations

import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    hopper,
)


class TestImagingCoreResize:
    def resize(self, im, size, f):
        # Image class independent version of resize.
        im.load()
        return im._new(im.im.resize(size, f))

    def test_nearest_mode(self):
        for mode in [
            "1",
            "P",
            "L",
            "I",
            "F",
            "RGB",
            "RGBA",
            "CMYK",
            "YCbCr",
            "I;16",
        ]:  # exotic mode
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.NEAREST)
            assert r.mode == mode
            assert r.size == (15, 12)
            assert r.im.bands == im.im.bands

    def test_convolution_modes(self):
        with pytest.raises(ValueError):
            self.resize(hopper("1"), (15, 12), Image.BILINEAR)
        with pytest.raises(ValueError):
            self.resize(hopper("P"), (15, 12), Image.BILINEAR)
        with pytest.raises(ValueError):
            self.resize(hopper("I;16"), (15, 12), Image.BILINEAR)
        for mode in ["L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr"]:
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.BILINEAR)
            assert r.mode == mode
            assert r.size == (15, 12)
            assert r.im.bands == im.im.bands

    def test_reduce_filters(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(hopper("RGB"), (15, 12), f)
            assert r.mode == "RGB"
            assert r.size == (15, 12)

    def test_enlarge_filters(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(hopper("RGB"), (212, 195), f)
            assert r.mode == "RGB"
            assert r.size == (212, 195)

    def test_endianness(self):
        # Make an image with one colored pixel, in one channel.
        # When resized, that channel should be the same as a GS image.
        # Other channels should be unaffected.
        # The R and A channels should not swap, which is indicative of
        # an endianness issues.

        samples = {
            "blank": Image.new("L", (2, 2), 0),
            "filled": Image.new("L", (2, 2), 255),
            "dirty": Image.new("L", (2, 2), 0),
        }
        samples["dirty"].putpixel((1, 1), 128)

        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            # samples resized with current filter
            references = {
                name: self.resize(ch, (4, 4), f) for name, ch in samples.items()
            }

            for mode, channels_set in [
                ("RGB", ("blank", "filled", "dirty")),
                ("RGBA", ("blank", "blank", "filled", "dirty")),
                ("LA", ("filled", "dirty")),
            ]:
                for channels in set(permutations(channels_set)):
                    # compile image from different channels permutations
                    im = Image.merge(mode, [samples[ch] for ch in channels])
                    resized = self.resize(im, (4, 4), f)

                    for i, ch in enumerate(resized.split()):
                        # check what resized channel in image is the same
                        # as separately resized channel
                        assert_image_equal(ch, references[channels[i]])

    def test_enlarge_zero(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(Image.new("RGB", (0, 0), "white"), (212, 195), f)
            assert r.mode == "RGB"
            assert r.size == (212, 195)
            assert r.getdata()[0] == (0, 0, 0)

    def test_unknown_filter(self):
        with pytest.raises(ValueError):
            self.resize(hopper(), (10, 10), 9)

    def test_cross_platform(self, tmp_path):
        # This test is intended for only check for consistent behaviour across
        # platforms. So if a future Pillow change requires that the test file
        # be updated, that is okay.
        im = hopper().resize((64, 64))
        temp_file = str(tmp_path / "temp.gif")
        im.save(temp_file)

        with Image.open(temp_file) as reloaded:
            assert_image_equal_tofile(reloaded, "Tests/images/hopper_resized.gif")


@pytest.fixture
def gradients_image():
    im = Image.open("Tests/images/radial_gradients.png")
    im.load()
    try:
        yield im
    finally:
        im.close()


class TestReducingGapResize:
    def test_reducing_gap_values(self, gradients_image):
        ref = gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=None)
        im = gradients_image.resize((52, 34), Image.BICUBIC)
        assert_image_equal(ref, im)

        with pytest.raises(ValueError):
            gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=0)

        with pytest.raises(ValueError):
            gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=0.99)

    def test_reducing_gap_1(self, gradients_image):
        for box, epsilon in [
            (None, 4),
            ((1.1, 2.2, 510.8, 510.9), 4),
            ((3, 10, 410, 256), 10),
        ]:
            ref = gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=1.0
            )

            with pytest.raises(AssertionError):
                assert_image_equal(ref, im)

            assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_2(self, gradients_image):
        for box, epsilon in [
            (None, 1.5),
            ((1.1, 2.2, 510.8, 510.9), 1.5),
            ((3, 10, 410, 256), 1),
        ]:
            ref = gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=2.0
            )

            with pytest.raises(AssertionError):
                assert_image_equal(ref, im)

            assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_3(self, gradients_image):
        for box, epsilon in [
            (None, 1),
            ((1.1, 2.2, 510.8, 510.9), 1),
            ((3, 10, 410, 256), 0.5),
        ]:
            ref = gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=3.0
            )

            with pytest.raises(AssertionError):
                assert_image_equal(ref, im)

            assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_8(self, gradients_image):
        for box in [None, (1.1, 2.2, 510.8, 510.9), (3, 10, 410, 256)]:
            ref = gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=8.0
            )

            assert_image_equal(ref, im)

    def test_box_filter(self, gradients_image):
        for box, epsilon in [
            ((0, 0, 512, 512), 5.5),
            ((0.9, 1.7, 128, 128), 9.5),
        ]:
            ref = gradients_image.resize((52, 34), Image.BOX, box=box)
            im = gradients_image.resize((52, 34), Image.BOX, box=box, reducing_gap=1.0)

            assert_image_similar(ref, im, epsilon)


class TestImageResize:
    def test_resize(self):
        def resize(mode, size):
            out = hopper(mode).resize(size)
            assert out.mode == mode
            assert out.size == size

        for mode in "1", "P", "L", "RGB", "I", "F":
            resize(mode, (112, 103))
            resize(mode, (188, 214))

        # Test unknown resampling filter
        with hopper() as im:
            with pytest.raises(ValueError):
                im.resize((10, 10), "unknown")

    def test_default_filter(self):
        for mode in "L", "RGB", "I", "F":
            im = hopper(mode)
            assert im.resize((20, 20), Image.BICUBIC) == im.resize((20, 20))

        for mode in "1", "P":
            im = hopper(mode)
            assert im.resize((20, 20), Image.NEAREST) == im.resize((20, 20))

        for mode in "I;16", "I;16L", "I;16B", "BGR;15", "BGR;16":
            im = hopper(mode)
            assert im.resize((20, 20), Image.NEAREST) == im.resize((20, 20))
