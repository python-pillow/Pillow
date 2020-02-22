# Test the ImageMorphology functionality
import pytest
from PIL import Image, ImageMorph, _imagingmorph

from .helper import PillowTestCase, assert_image_equal, hopper


class MorphTests(PillowTestCase):
    def setUp(self):
        self.A = self.string_to_img(
            """
            .......
            .......
            ..111..
            ..111..
            ..111..
            .......
            .......
            """
        )

    def img_to_string(self, im):
        """Turn a (small) binary image into a string representation"""
        chars = ".1"
        width, height = im.size
        return "\n".join(
            "".join(chars[im.getpixel((c, r)) > 0] for c in range(width))
            for r in range(height)
        )

    def string_to_img(self, image_string):
        """Turn a string image representation into a binary image"""
        rows = [s for s in image_string.replace(" ", "").split("\n") if len(s)]
        height = len(rows)
        width = len(rows[0])
        im = Image.new("L", (width, height))
        for i in range(width):
            for j in range(height):
                c = rows[j][i]
                v = c in "X1"
                im.putpixel((i, j), v)

        return im

    def img_string_normalize(self, im):
        return self.img_to_string(self.string_to_img(im))

    def assert_img_equal(self, A, B):
        assert self.img_to_string(A) == self.img_to_string(B)

    def assert_img_equal_img_string(self, A, Bstring):
        assert self.img_to_string(A) == self.img_string_normalize(Bstring)

    def test_str_to_img(self):
        with Image.open("Tests/images/morph_a.png") as im:
            assert_image_equal(self.A, im)

    def create_lut(self):
        for op in ("corner", "dilation4", "dilation8", "erosion4", "erosion8", "edge"):
            lb = ImageMorph.LutBuilder(op_name=op)
            lut = lb.build_lut()
            with open("Tests/images/%s.lut" % op, "wb") as f:
                f.write(lut)

    # create_lut()
    def test_lut(self):
        for op in ("corner", "dilation4", "dilation8", "erosion4", "erosion8", "edge"):
            lb = ImageMorph.LutBuilder(op_name=op)
            assert lb.get_lut() is None

            lut = lb.build_lut()
            with open("Tests/images/%s.lut" % op, "rb") as f:
                assert lut == bytearray(f.read())

    def test_no_operator_loaded(self):
        mop = ImageMorph.MorphOp()
        with pytest.raises(Exception) as e:
            mop.apply(None)
        assert str(e.value) == "No operator loaded"
        with pytest.raises(Exception) as e:
            mop.match(None)
        assert str(e.value) == "No operator loaded"
        with pytest.raises(Exception) as e:
            mop.save_lut(None)
        assert str(e.value) == "No operator loaded"

    # Test the named patterns
    def test_erosion8(self):
        # erosion8
        mop = ImageMorph.MorphOp(op_name="erosion8")
        count, Aout = mop.apply(self.A)
        assert count == 8
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .......
                                         .......
                                         ...1...
                                         .......
                                         .......
                                         .......
                                         """,
        )

    def test_dialation8(self):
        # dialation8
        mop = ImageMorph.MorphOp(op_name="dilation8")
        count, Aout = mop.apply(self.A)
        assert count == 16
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .11111.
                                         .11111.
                                         .11111.
                                         .11111.
                                         .11111.
                                         .......
                                         """,
        )

    def test_erosion4(self):
        # erosion4
        mop = ImageMorph.MorphOp(op_name="dilation4")
        count, Aout = mop.apply(self.A)
        assert count == 12
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         ..111..
                                         .11111.
                                         .11111.
                                         .11111.
                                         ..111..
                                         .......
                                         """,
        )

    def test_edge(self):
        # edge
        mop = ImageMorph.MorphOp(op_name="edge")
        count, Aout = mop.apply(self.A)
        assert count == 1
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .......
                                         ..111..
                                         ..1.1..
                                         ..111..
                                         .......
                                         .......
                                         """,
        )

    def test_corner(self):
        # Create a corner detector pattern
        mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "4:(00. 01. ...)->1"])
        count, Aout = mop.apply(self.A)
        assert count == 5
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .......
                                         ..1.1..
                                         .......
                                         ..1.1..
                                         .......
                                         .......
                                         """,
        )

        # Test the coordinate counting with the same operator
        coords = mop.match(self.A)
        assert len(coords) == 4
        assert tuple(coords) == ((2, 2), (4, 2), (2, 4), (4, 4))

        coords = mop.get_on_pixels(Aout)
        assert len(coords) == 4
        assert tuple(coords) == ((2, 2), (4, 2), (2, 4), (4, 4))

    def test_mirroring(self):
        # Test 'M' for mirroring
        mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "M:(00. 01. ...)->1"])
        count, Aout = mop.apply(self.A)
        assert count == 7
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .......
                                         ..1.1..
                                         .......
                                         .......
                                         .......
                                         .......
                                         """,
        )

    def test_negate(self):
        # Test 'N' for negate
        mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "N:(00. 01. ...)->1"])
        count, Aout = mop.apply(self.A)
        assert count == 8
        self.assert_img_equal_img_string(
            Aout,
            """
                                         .......
                                         .......
                                         ..1....
                                         .......
                                         .......
                                         .......
                                         .......
                                         """,
        )

    def test_non_binary_images(self):
        im = hopper("RGB")
        mop = ImageMorph.MorphOp(op_name="erosion8")

        with pytest.raises(Exception) as e:
            mop.apply(im)
        assert str(e.value) == "Image must be binary, meaning it must use mode L"
        with pytest.raises(Exception) as e:
            mop.match(im)
        assert str(e.value) == "Image must be binary, meaning it must use mode L"
        with pytest.raises(Exception) as e:
            mop.get_on_pixels(im)
        assert str(e.value) == "Image must be binary, meaning it must use mode L"

    def test_add_patterns(self):
        # Arrange
        lb = ImageMorph.LutBuilder(op_name="corner")
        assert lb.patterns == ["1:(... ... ...)->0", "4:(00. 01. ...)->1"]
        new_patterns = ["M:(00. 01. ...)->1", "N:(00. 01. ...)->1"]

        # Act
        lb.add_patterns(new_patterns)

        # Assert
        assert lb.patterns == [
            "1:(... ... ...)->0",
            "4:(00. 01. ...)->1",
            "M:(00. 01. ...)->1",
            "N:(00. 01. ...)->1",
        ]

    def test_unknown_pattern(self):
        with pytest.raises(Exception):
            ImageMorph.LutBuilder(op_name="unknown")

    def test_pattern_syntax_error(self):
        # Arrange
        lb = ImageMorph.LutBuilder(op_name="corner")
        new_patterns = ["a pattern with a syntax error"]
        lb.add_patterns(new_patterns)

        # Act / Assert
        with pytest.raises(Exception) as e:
            lb.build_lut()
        assert str(e.value) == 'Syntax error in pattern "a pattern with a syntax error"'

    def test_load_invalid_mrl(self):
        # Arrange
        invalid_mrl = "Tests/images/hopper.png"
        mop = ImageMorph.MorphOp()

        # Act / Assert
        with pytest.raises(Exception) as e:
            mop.load_lut(invalid_mrl)
        assert str(e.value) == "Wrong size operator file!"

    def test_roundtrip_mrl(self):
        # Arrange
        tempfile = self.tempfile("temp.mrl")
        mop = ImageMorph.MorphOp(op_name="corner")
        initial_lut = mop.lut

        # Act
        mop.save_lut(tempfile)
        mop.load_lut(tempfile)

        # Act / Assert
        assert mop.lut == initial_lut

    def test_set_lut(self):
        # Arrange
        lb = ImageMorph.LutBuilder(op_name="corner")
        lut = lb.build_lut()
        mop = ImageMorph.MorphOp()

        # Act
        mop.set_lut(lut)

        # Assert
        assert mop.lut == lut

    def test_wrong_mode(self):
        lut = ImageMorph.LutBuilder(op_name="corner").build_lut()
        imrgb = Image.new("RGB", (10, 10))
        iml = Image.new("L", (10, 10))

        with pytest.raises(RuntimeError):
            _imagingmorph.apply(bytes(lut), imrgb.im.id, iml.im.id)

        with pytest.raises(RuntimeError):
            _imagingmorph.apply(bytes(lut), iml.im.id, imrgb.im.id)

        with pytest.raises(RuntimeError):
            _imagingmorph.match(bytes(lut), imrgb.im.id)

        # Should not raise
        _imagingmorph.match(bytes(lut), iml.im.id)
