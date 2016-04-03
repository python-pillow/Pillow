from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageDraw
from io import BytesIO
import os
import sys
import copy

FONT_PATH = "Tests/fonts/FreeMono.ttf"
FONT_SIZE = 20

TEST_TEXT = "hey you\nyou are awesome\nthis looks awkward"


try:
    from PIL import ImageFont
    ImageFont.core.getfont  # check if freetype is available

    class SimplePatcher(object):
        def __init__(self, parent_obj, attr_name, value):
            self._parent_obj = parent_obj
            self._attr_name = attr_name
            self._saved = None
            self._is_saved = False
            self._value = value

        def __enter__(self):
            # Patch the attr on the object
            if hasattr(self._parent_obj, self._attr_name):
                self._saved = getattr(self._parent_obj, self._attr_name)
                setattr(self._parent_obj, self._attr_name, self._value)
                self._is_saved = True
            else:
                setattr(self._parent_obj, self._attr_name, self._value)
                self._is_saved = False

        def __exit__(self, type, value, traceback):
            # Restore the original value
            if self._is_saved:
                setattr(self._parent_obj, self._attr_name, self._saved)
            else:
                delattr(self._parent_obj, self._attr_name)

    class TestImageFont(PillowTestCase):

        def test_sanity(self):
            self.assertRegexpMatches(
                ImageFont.core.freetype2_version, "\d+\.\d+\.\d+$")

        def test_font_properties(self):
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            self.assertEqual(ttf.path, FONT_PATH)
            self.assertEqual(ttf.size, FONT_SIZE)

            ttf_copy = ttf.font_variant()
            self.assertEqual(ttf_copy.path, FONT_PATH)
            self.assertEqual(ttf_copy.size, FONT_SIZE)

            ttf_copy = ttf.font_variant(size=FONT_SIZE+1)
            self.assertEqual(ttf_copy.size, FONT_SIZE+1)

            second_font_path = "Tests/fonts/DejaVuSans.ttf"
            ttf_copy = ttf.font_variant(font=second_font_path)
            self.assertEqual(ttf_copy.path, second_font_path)

        def test_font_with_name(self):
            ImageFont.truetype(FONT_PATH, FONT_SIZE)
            self._render(FONT_PATH)
            self._clean()

        def _font_as_bytes(self):
            with open(FONT_PATH, 'rb') as f:
                font_bytes = BytesIO(f.read())
            return font_bytes

        def test_font_with_filelike(self):
            ImageFont.truetype(self._font_as_bytes(), FONT_SIZE)
            self._render(self._font_as_bytes())
            # Usage note:  making two fonts from the same buffer fails.
            # shared_bytes = self._font_as_bytes()
            # self._render(shared_bytes)
            # self.assertRaises(Exception, lambda: _render(shared_bytes))
            self._clean()

        def test_font_with_open_file(self):
            with open(FONT_PATH, 'rb') as f:
                self._render(f)
            self._clean()

        def _render(self, font):
            txt = "Hello World!"
            ttf = ImageFont.truetype(font, FONT_SIZE)
            ttf.getsize(txt)

            img = Image.new("RGB", (256, 64), "white")
            d = ImageDraw.Draw(img)
            d.text((10, 10), txt, font=ttf, fill='black')

            img.save('font.png')
            return img

        def _clean(self):
            os.unlink('font.png')

        def test_render_equal(self):
            img_path = self._render(FONT_PATH)
            with open(FONT_PATH, 'rb') as f:
                font_filelike = BytesIO(f.read())
            img_filelike = self._render(font_filelike)

            self.assert_image_equal(img_path, img_filelike)
            self._clean()

        def test_textsize_equal(self):
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            txt = "Hello World!"
            size = draw.textsize(txt, ttf)
            draw.text((10, 10), txt, font=ttf)
            draw.rectangle((10, 10, 10 + size[0], 10 + size[1]))
            del draw

            target = 'Tests/images/rectangle_surrounding_text.png'
            target_img = Image.open(target)
            self.assert_image_similar(im, target_img, .5)

        def test_render_multiline(self):
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            line_spacing = draw.textsize('A', font=ttf)[1] + 4
            lines = TEST_TEXT.split("\n")
            y = 0
            for line in lines:
                draw.text((0, y), line, font=ttf)
                y += line_spacing

            target = 'Tests/images/multiline_text.png'
            target_img = Image.open(target)

            # some versions of freetype have different horizontal spacing.
            # setting a tight epsilon, I'm showing the original test failure
            # at epsilon = ~38.
            self.assert_image_similar(im, target_img, .5)

        def test_render_multiline_text(self):
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            # Test that text() correctly connects to multiline_text()
            # and that align defaults to left
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)
            draw.text((0, 0), TEST_TEXT, font=ttf)

            target = 'Tests/images/multiline_text.png'
            target_img = Image.open(target)

            self.assert_image_similar(im, target_img, .5)

            # Test that text() can pass on additional arguments
            # to multiline_text()
            draw.text((0, 0), TEST_TEXT, fill=None, font=ttf, anchor=None,
                      spacing=4, align="left")
            draw.text((0, 0), TEST_TEXT, None, ttf, None, 4, "left")
            del draw

            # Test align center and right
            for align, ext in {"center": "_center",
                               "right": "_right"}.items():
                im = Image.new(mode='RGB', size=(300, 100))
                draw = ImageDraw.Draw(im)
                draw.multiline_text((0, 0), TEST_TEXT, font=ttf, align=align)
                del draw

                target = 'Tests/images/multiline_text'+ext+'.png'
                target_img = Image.open(target)

                self.assert_image_similar(im, target_img, .5)

        def test_unknown_align(self):
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            # Act/Assert
            self.assertRaises(AssertionError,
                              lambda: draw.multiline_text((0, 0), TEST_TEXT,
                                                          font=ttf,
                                                          align="unknown"))

        def test_multiline_size(self):
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)

            # Test that textsize() correctly connects to multiline_textsize()
            self.assertEqual(draw.textsize(TEST_TEXT, font=ttf),
                             draw.multiline_textsize(TEST_TEXT, font=ttf))

            # Test that textsize() can pass on additional arguments
            # to multiline_textsize()
            draw.textsize(TEST_TEXT, font=ttf, spacing=4)
            draw.textsize(TEST_TEXT, ttf, 4)
            del draw

        def test_multiline_width(self):
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)

            self.assertEqual(draw.textsize("longest line", font=ttf)[0],
                             draw.multiline_textsize("longest line\nline",
                                                     font=ttf)[0])
            del draw

        def test_multiline_spacing(self):
            ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)
            draw.multiline_text((0, 0), TEST_TEXT, font=ttf, spacing=10)
            del draw

            target = 'Tests/images/multiline_text_spacing.png'
            target_img = Image.open(target)

            self.assert_image_similar(im, target_img, .5)

        def test_rotated_transposed_font(self):
            img_grey = Image.new("L", (100, 100))
            draw = ImageDraw.Draw(img_grey)
            word = "testing"
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            orientation = Image.ROTATE_90
            transposed_font = ImageFont.TransposedFont(
                font, orientation=orientation)

            # Original font
            draw.font = font
            box_size_a = draw.textsize(word)

            # Rotated font
            draw.font = transposed_font
            box_size_b = draw.textsize(word)
            del draw

            # Check (w,h) of box a is (h,w) of box b
            self.assertEqual(box_size_a[0], box_size_b[1])
            self.assertEqual(box_size_a[1], box_size_b[0])

        def test_unrotated_transposed_font(self):
            img_grey = Image.new("L", (100, 100))
            draw = ImageDraw.Draw(img_grey)
            word = "testing"
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            orientation = None
            transposed_font = ImageFont.TransposedFont(
                font, orientation=orientation)

            # Original font
            draw.font = font
            box_size_a = draw.textsize(word)

            # Rotated font
            draw.font = transposed_font
            box_size_b = draw.textsize(word)
            del draw

            # Check boxes a and b are same size
            self.assertEqual(box_size_a, box_size_b)

        def test_rotated_transposed_font_get_mask(self):
            # Arrange
            text = "mask this"
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            orientation = Image.ROTATE_90
            transposed_font = ImageFont.TransposedFont(
                font, orientation=orientation)

            # Act
            mask = transposed_font.getmask(text)

            # Assert
            self.assertEqual(mask.size, (13, 108))

        def test_unrotated_transposed_font_get_mask(self):
            # Arrange
            text = "mask this"
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            orientation = None
            transposed_font = ImageFont.TransposedFont(
                font, orientation=orientation)

            # Act
            mask = transposed_font.getmask(text)

            # Assert
            self.assertEqual(mask.size, (108, 13))

        def test_free_type_font_get_name(self):
            # Arrange
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            # Act
            name = font.getname()

            # Assert
            self.assertEqual(('FreeMono', 'Regular'), name)

        def test_free_type_font_get_metrics(self):
            # Arrange
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            # Act
            ascent, descent = font.getmetrics()

            # Assert
            self.assertIsInstance(ascent, int)
            self.assertIsInstance(descent, int)
            self.assertEqual((ascent, descent), (16, 4))  # too exact check?

        def test_free_type_font_get_offset(self):
            # Arrange
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            text = "offset this"

            # Act
            offset = font.getoffset(text)

            # Assert
            self.assertEqual(offset, (0, 3))

        def test_free_type_font_get_mask(self):
            # Arrange
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            text = "mask this"

            # Act
            mask = font.getmask(text)

            # Assert
            self.assertEqual(mask.size, (108, 13))

        def test_load_path_not_found(self):
            # Arrange
            filename = "somefilenamethatdoesntexist.ttf"

            # Act/Assert
            self.assertRaises(IOError, lambda: ImageFont.load_path(filename))

        def test_default_font(self):
            # Arrange
            txt = 'This is a "better than nothing" default font.'
            im = Image.new(mode='RGB', size=(300, 100))
            draw = ImageDraw.Draw(im)

            target = 'Tests/images/default_font.png'
            target_img = Image.open(target)

            # Act
            default_font = ImageFont.load_default()
            draw.text((10, 10), txt, font=default_font)
            del draw

            # Assert
            self.assert_image_equal(im, target_img)

        def _test_fake_loading_font(self, path_to_fake, fontname):
            # Make a copy of FreeTypeFont so we can patch the original
            free_type_font = copy.deepcopy(ImageFont.FreeTypeFont)
            with SimplePatcher(ImageFont, '_FreeTypeFont', free_type_font):
                def loadable_font(filepath, size, index, encoding):
                    if filepath == path_to_fake:
                        return ImageFont._FreeTypeFont(FONT_PATH, size, index,
                                                       encoding)
                    return ImageFont._FreeTypeFont(filepath, size, index,
                                                   encoding)
                with SimplePatcher(ImageFont, 'FreeTypeFont', loadable_font):
                    font = ImageFont.truetype(fontname)
                    # Make sure it's loaded
                    name = font.getname()
                    self.assertEqual(('FreeMono', 'Regular'), name)

        @unittest.skipIf(sys.platform.startswith('win32'),
                         "requires Unix or MacOS")
        def test_find_linux_font(self):
            # A lot of mocking here - this is more for hitting code and
            # catching syntax like errors
            font_directory = '/usr/local/share/fonts'
            with SimplePatcher(sys, 'platform', 'linux'):
                patched_env = copy.deepcopy(os.environ)
                patched_env['XDG_DATA_DIRS'] = '/usr/share/:/usr/local/share/'
                with SimplePatcher(os, 'environ', patched_env):
                    def fake_walker(path):
                        if path == font_directory:
                            return [(path, [], [
                                'Arial.ttf', 'Single.otf', 'Duplicate.otf',
                                'Duplicate.ttf'], )]
                        return [(path, [], ['some_random_font.ttf'], )]
                    with SimplePatcher(os, 'walk', fake_walker):
                        # Test that the font loads both with and without the
                        # extension
                        self._test_fake_loading_font(
                            font_directory+'/Arial.ttf', 'Arial.ttf')
                        self._test_fake_loading_font(
                            font_directory+'/Arial.ttf', 'Arial')

                        # Test that non-ttf fonts can be found without the
                        # extension
                        self._test_fake_loading_font(
                            font_directory+'/Single.otf', 'Single')

                        # Test that ttf fonts are preferred if the extension is
                        # not specified
                        self._test_fake_loading_font(
                            font_directory+'/Duplicate.ttf', 'Duplicate')

        @unittest.skipIf(sys.platform.startswith('win32'),
                         "requires Unix or MacOS")
        def test_find_osx_font(self):
            # Like the linux test, more cover hitting code rather than testing
            # correctness.
            font_directory = '/System/Library/Fonts'
            with SimplePatcher(sys, 'platform', 'darwin'):
                def fake_walker(path):
                    if path == font_directory:
                        return [(path, [],
                                ['Arial.ttf', 'Single.otf',
                                 'Duplicate.otf', 'Duplicate.ttf'], )]
                    return [(path, [], ['some_random_font.ttf'], )]
                with SimplePatcher(os, 'walk', fake_walker):
                    self._test_fake_loading_font(
                        font_directory+'/Arial.ttf', 'Arial.ttf')
                    self._test_fake_loading_font(
                        font_directory+'/Arial.ttf', 'Arial')
                    self._test_fake_loading_font(
                        font_directory+'/Single.otf', 'Single')
                    self._test_fake_loading_font(
                        font_directory+'/Duplicate.ttf', 'Duplicate')

        def test_imagefont_getters(self):
            # Arrange
            t = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            # Act / Assert
            self.assertEqual(t.getmetrics(), (16, 4))
            self.assertEqual(t.font.ascent, 16)
            self.assertEqual(t.font.descent, 4)
            self.assertEqual(t.font.height, 20)
            self.assertEqual(t.font.x_ppem, 20)
            self.assertEqual(t.font.y_ppem, 20)
            self.assertEqual(t.font.glyphs, 4177)
            self.assertEqual(t.getsize('A'), (12, 16))
            self.assertEqual(t.getsize('AB'), (24, 16))
            self.assertEqual(t.getsize('M'), (12, 16))
            self.assertEqual(t.getsize('y'), (12, 20))
            self.assertEqual(t.getsize('a'), (12, 16))


except ImportError:
    class TestImageFont(PillowTestCase):
        def test_skip(self):
            self.skipTest("ImportError")


if __name__ == '__main__':
    unittest.main()

# End of file
