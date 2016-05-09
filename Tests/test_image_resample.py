from helper import unittest, PillowTestCase, hopper
from PIL import Image, ImageDraw


class TestImagingResampleVulnerability(PillowTestCase):
    # see https://github.com/python-pillow/Pillow/issues/1710
    def test_overflow(self):
        im = hopper('L')
        xsize = 0x100000008 // 4
        ysize = 1000  # unimportant
        try:
            # any resampling filter will do here
            im.im.resize((xsize, ysize), Image.LINEAR)
            self.fail("Resize should raise MemoryError on invalid xsize")
        except MemoryError:
            self.assertTrue(True, "Should raise MemoryError")

    def test_invalid_size(self):
        im = hopper()

        im.resize((100, 100))
        self.assertTrue(True, "Should not Crash")

        try:
            im.resize((-100, 100))
            self.fail("Resize should raise a value error on x negative size")
        except ValueError:
            self.assertTrue(True, "Should raise ValueError")

        try:
            im.resize((100, -100))
            self.fail("Resize should raise a value error on y negative size")
        except ValueError:
            self.assertTrue(True, "Should raise ValueError")


class TestImagingCoreResampleAccuracy(PillowTestCase):
    def make_case(self, size, color):
        """Makes a sample image with two dark and two bright squares.
        For example:
        e0 e0 1f 1f
        e0 e0 1f 1f
        1f 1f e0 e0
        1f 1f e0 e0
        """
        dark = (255 - color, 255 - color, 255 - color, 255 - color)
        bright = (color, color, color, color)

        i = Image.new('RGBX', size, dark)
        rectangle = ImageDraw.Draw(i).rectangle
        rectangle((0, 0, size[0] // 2 - 1, size[1] // 2 - 1), bright)
        rectangle((size[0] // 2, size[1] // 2, size[0], size[1]), bright)
        return i

    def make_sample(self, data, size):
        """Restores a sample image from given data string which contains
        hex-encoded pixels from the top left fourth of a sample.
        """
        data = data.replace(' ', '')
        sample = Image.new('L', size)
        s_px = sample.load()
        w, h = size[0] // 2, size[1] // 2
        for y in range(h):
            for x in range(w):
                val = int(data[(y * w + x) * 2:(y * w + x + 1) * 2], 16)
                s_px[x, y] = val
                s_px[size[0] - x - 1, size[1] - y - 1] = val
                s_px[x, size[1] - y - 1] = 255 - val
                s_px[size[0] - x - 1, y] = 255 - val
        return sample

    def check_case(self, case, sample):
        for channel in case.split():
            s_px = sample.load()
            c_px = channel.load()
            for y in range(case.size[1]):
                for x in range(case.size[0]):
                    if c_px[x, y] != s_px[x, y]:
                        message = '\nHave: \n{}\n\nExpected: \n{}'.format(
                            self.serialize_image(channel),
                            self.serialize_image(sample),
                        )
                        self.assertEqual(s_px[x, y], c_px[x, y], message)

    def serialize_image(self, image):
        s_px = image.load()
        return '\n'.join(
            ' '.join(
                '{:02x}'.format(s_px[x, y])
                for x in range(image.size[0])
            )
            for y in range(image.size[1])
        )

    def test_reduce_bilinear(self):
        case = self.make_case((8, 8), 0xe1)
        data = ('e1 c9'
                'c9 b7')
        self.check_case(
            case.resize((4, 4), Image.BILINEAR),
            self.make_sample(data, (4, 4)))

    def test_reduce_bicubic(self):
        case = self.make_case((12, 12), 0xe1)
        data = ('e1 e3 d4'
                'e3 e5 d6'
                'd4 d6 c9')
        self.check_case(
            case.resize((6, 6), Image.BICUBIC),
            self.make_sample(data, (6, 6)))

    def test_reduce_lanczos(self):
        case = self.make_case((16, 16), 0xe1)
        data = ('e1 e0 e4 d7'
                'e0 df e3 d6'
                'e4 e3 e7 da'
                'd7 d6 d9 ce')
        self.check_case(
            case.resize((8, 8), Image.LANCZOS),
            self.make_sample(data, (8, 8)))

    def test_enlarge_bilinear(self):
        case = self.make_case((2, 2), 0xe1)
        data = ('e1 b0'
                'b0 98')
        self.check_case(
            case.resize((4, 4), Image.BILINEAR),
            self.make_sample(data, (4, 4)))

    def test_enlarge_bicubic(self):
        case = self.make_case((4, 4), 0xe1)
        data = ('e1 e5 ee b9'
                'e5 e9 f3 bc'
                'ee f3 fd c1'
                'b9 bc c1 a2')
        self.check_case(
            case.resize((8, 8), Image.BICUBIC),
            self.make_sample(data, (8, 8)))

    def test_enlarge_lanczos(self):
        case = self.make_case((6, 6), 0xe1)
        data = ('e1 e0 db ed f5 b8'
                'e0 df da ec f3 b7'
                'db db d6 e7 ee b5'
                'ed ec e6 fb ff bf'
                'f5 f4 ee ff ff c4'
                'b8 b7 b4 bf c4 a0')
        self.check_case(
            case.resize((12, 12), Image.LANCZOS),
            self.make_sample(data, (12, 12)))


class CoreResampleConsistencyTest(PillowTestCase):
    def make_case(self, mode, fill):
        im = Image.new(mode, (512, 9), fill)
        return (im.resize((9, 512), Image.LANCZOS), im.load()[0, 0])

    def run_case(self, case):
        channel, color = case
        px = channel.load()
        for x in range(channel.size[0]):
            for y in range(channel.size[1]):
                if px[x, y] != color:
                    message = "{} != {} for pixel {}".format(
                        px[x, y], color, (x, y))
                    self.assertEqual(px[x, y], color, message)

    def test_8u(self):
        im, color = self.make_case('RGB', (0, 64, 255))
        r, g, b = im.split()
        self.run_case((r, color[0]))
        self.run_case((g, color[1]))
        self.run_case((b, color[2]))
        self.run_case(self.make_case('L', 12))

    def test_32i(self):
        self.run_case(self.make_case('I', 12))
        self.run_case(self.make_case('I', 0x7fffffff))
        self.run_case(self.make_case('I', -12))
        self.run_case(self.make_case('I', -1 << 31))

    def test_32f(self):
        self.run_case(self.make_case('F', 1))
        self.run_case(self.make_case('F', 3.40282306074e+38))
        self.run_case(self.make_case('F', 1.175494e-38))
        self.run_case(self.make_case('F', 1.192093e-07))


class CoreResampleAlphaCorrectTest(PillowTestCase):
    def test_levels(self):
        i = Image.new('RGBA', (256, 16))
        px = i.load()
        for y in range(i.size[1]):
            for x in range(i.size[0]):
                px[x, y] = (x, x, x, 255 - y * 16)

        i = i.resize((512, 32), Image.BILINEAR)
        px = i.load()
        for y in range(i.size[1]):
            used_colors = set(px[x, y][0] for x in range(i.size[0]))
            self.assertEqual(256, len(used_colors),
                'All colors should present in resized image. '
                'Only {0} on {1} line.'.format(len(used_colors), y))

    def test_dirty_pixels(self):
        i = Image.new('RGBA', (64, 64), (0, 0, 255, 0))
        px = i.load()
        for y in range(i.size[1] // 4, i.size[1] // 4 * 3):
            for x in range(i.size[0] // 4, i.size[0] // 4 * 3):
                px[x, y] = (255, 255, 0, 128)


        for im in [
            i.resize((20, 20), Image.BILINEAR),
            i.resize((20, 20), Image.BICUBIC),
            i.resize((20, 20), Image.LANCZOS),
        ]:
            px = im.load()
            for y in range(im.size[1]):
                for x in range(im.size[0]):
                    if px[x, y][3] != 0:
                        if px[x, y][:3] != (255, 256, 0):
                            self.assertEqual(px[x, y][:3], (255, 255, 0))


if __name__ == '__main__':
    unittest.main()
