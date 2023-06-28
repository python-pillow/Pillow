import pytest

from PIL import Image

from .helper import hopper

TEST_FILE = "Tests/images/hopper.ppm"

ORIGINAL_LIMIT = Image.MAX_IMAGE_PIXELS


class TestDecompressionBomb:
    def teardown_method(self, method):
        Image.MAX_IMAGE_PIXELS = ORIGINAL_LIMIT

    def test_no_warning_small_file(self):
        # Implicit assert: no warning.
        # A warning would cause a failure.
        with Image.open(TEST_FILE):
            pass

    def test_no_warning_no_limit(self):
        # Arrange
        # Turn limit off
        Image.MAX_IMAGE_PIXELS = None
        assert Image.MAX_IMAGE_PIXELS is None

        # Act / Assert
        # Implicit assert: no warning.
        # A warning would cause a failure.
        with Image.open(TEST_FILE):
            pass

    def test_warning(self):
        # Set limit to trigger warning on the test file
        Image.MAX_IMAGE_PIXELS = 128 * 128 - 1
        assert Image.MAX_IMAGE_PIXELS == 128 * 128 - 1

        with pytest.warns(Image.DecompressionBombWarning):
            with Image.open(TEST_FILE):
                pass

    def test_exception(self):
        # Set limit to trigger exception on the test file
        Image.MAX_IMAGE_PIXELS = 64 * 128 - 1
        assert Image.MAX_IMAGE_PIXELS == 64 * 128 - 1

        with pytest.raises(Image.DecompressionBombError):
            with Image.open(TEST_FILE):
                pass

    def test_exception_ico(self):
        with pytest.raises(Image.DecompressionBombError):
            with Image.open("Tests/images/decompression_bomb.ico"):
                pass

    def test_exception_gif(self):
        with pytest.raises(Image.DecompressionBombError):
            with Image.open("Tests/images/decompression_bomb.gif"):
                pass

    def test_exception_gif_extents(self):
        with Image.open("Tests/images/decompression_bomb_extents.gif") as im:
            with pytest.raises(Image.DecompressionBombError):
                im.seek(1)

    def test_exception_gif_zero_width(self):
        # Set limit to trigger exception on the test file
        Image.MAX_IMAGE_PIXELS = 4 * 64 * 128
        assert Image.MAX_IMAGE_PIXELS == 4 * 64 * 128

        with pytest.raises(Image.DecompressionBombError):
            with Image.open("Tests/images/zero_width.gif"):
                pass

    def test_exception_bmp(self):
        with pytest.raises(Image.DecompressionBombError):
            with Image.open("Tests/images/bmp/b/reallybig.bmp"):
                pass


class TestDecompressionCrop:
    @classmethod
    def setup_class(cls):
        width, height = 128, 128
        Image.MAX_IMAGE_PIXELS = height * width * 4 - 1

    @classmethod
    def teardown_class(cls):
        Image.MAX_IMAGE_PIXELS = ORIGINAL_LIMIT

    def test_enlarge_crop(self):
        # Crops can extend the extents, therefore we should have the
        # same decompression bomb warnings on them.
        with hopper() as src:
            box = (0, 0, src.width * 2, src.height * 2)
            with pytest.warns(Image.DecompressionBombWarning):
                src.crop(box)

    def test_crop_decompression_checks(self):
        im = Image.new("RGB", (100, 100))

        for value in ((-9999, -9999, -9990, -9990), (-999, -999, -990, -990)):
            assert im.crop(value).size == (9, 9)

        with pytest.warns(Image.DecompressionBombWarning):
            im.crop((-160, -160, 99, 99))

        with pytest.raises(Image.DecompressionBombError):
            im.crop((-99909, -99990, 99999, 99999))
