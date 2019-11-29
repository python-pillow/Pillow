import os

from PIL import Image

from .helper import PillowTestCase

base = os.path.join("Tests", "images", "bmp")


class TestBmpReference(PillowTestCase):
    def get_files(self, d, ext=".bmp"):
        return [
            os.path.join(base, d, f)
            for f in os.listdir(os.path.join(base, d))
            if ext in f
        ]

    def test_bad(self):
        """ These shouldn't crash/dos, but they shouldn't return anything
        either """
        for f in self.get_files("b"):

            def open(f):
                try:
                    with Image.open(f) as im:
                        im.load()
                except Exception:  # as msg:
                    pass

            # Assert that there is no unclosed file warning
            self.assert_warning(None, open, f)

    def test_questionable(self):
        """ These shouldn't crash/dos, but it's not well defined that these
        are in spec """
        supported = [
            "pal8os2v2.bmp",
            "rgb24prof.bmp",
            "pal1p1.bmp",
            "pal8offs.bmp",
            "rgb24lprof.bmp",
            "rgb32fakealpha.bmp",
            "rgb24largepal.bmp",
            "pal8os2sp.bmp",
            "rgb32bf-xbgr.bmp",
        ]
        for f in self.get_files("q"):
            try:
                with Image.open(f) as im:
                    im.load()
                if os.path.basename(f) not in supported:
                    print("Please add %s to the partially supported bmp specs." % f)
            except Exception:  # as msg:
                if os.path.basename(f) in supported:
                    raise

    def test_good(self):
        """ These should all work. There's a set of target files in the
        html directory that we can compare against. """

        # Target files, if they're not just replacing the extension
        file_map = {
            "pal1wb.bmp": "pal1.png",
            "pal4rle.bmp": "pal4.png",
            "pal8-0.bmp": "pal8.png",
            "pal8rle.bmp": "pal8.png",
            "pal8topdown.bmp": "pal8.png",
            "pal8nonsquare.bmp": "pal8nonsquare-v.png",
            "pal8os2.bmp": "pal8.png",
            "pal8os2sp.bmp": "pal8.png",
            "pal8os2v2.bmp": "pal8.png",
            "pal8os2v2-16.bmp": "pal8.png",
            "pal8v4.bmp": "pal8.png",
            "pal8v5.bmp": "pal8.png",
            "rgb16-565pal.bmp": "rgb16-565.png",
            "rgb24pal.bmp": "rgb24.png",
            "rgb32.bmp": "rgb24.png",
            "rgb32bf.bmp": "rgb24.png",
        }

        def get_compare(f):
            name = os.path.split(f)[1]
            if name in file_map:
                return os.path.join(base, "html", file_map[name])
            name = os.path.splitext(name)[0]
            return os.path.join(base, "html", "%s.png" % name)

        for f in self.get_files("g"):
            try:
                with Image.open(f) as im:
                    im.load()
                    with Image.open(get_compare(f)) as compare:
                        compare.load()
                        if im.mode == "P":
                            # assert image similar doesn't really work
                            # with paletized image, since the palette might
                            # be differently ordered for an equivalent image.
                            im = im.convert("RGBA")
                            compare = im.convert("RGBA")
                        self.assert_image_similar(im, compare, 5)

            except Exception as msg:
                # there are three here that are unsupported:
                unsupported = (
                    os.path.join(base, "g", "rgb32bf.bmp"),
                    os.path.join(base, "g", "pal8rle.bmp"),
                    os.path.join(base, "g", "pal4rle.bmp"),
                )
                if f not in unsupported:
                    self.fail("Unsupported Image {}: {}".format(f, msg))
