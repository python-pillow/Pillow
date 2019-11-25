import unittest

from PIL import Image, ImageDraw, ImageFont, features

from .helper import PillowTestCase

FONT_SIZE = 20
FONT_PATH = "Tests/fonts/DejaVuSans.ttf"


@unittest.skipUnless(features.check("raqm"), "Raqm Library is not installed.")
class TestImagecomplextext(PillowTestCase):
    def test_english(self):
        # smoke test, this should not fail
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "TEST", font=ttf, fill=500, direction="ltr")

    def test_complex_text(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "اهلا عمان", font=ttf, fill=500)

        target = "Tests/images/test_text.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_y_offset(self):
        ttf = ImageFont.truetype("Tests/fonts/NotoNastaliqUrdu-Regular.ttf", FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "العالم العربي", font=ttf, fill=500)

        target = "Tests/images/test_y_offset.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 1.7)

    def test_complex_unicode_text(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "السلام عليكم", font=ttf, fill=500)

        target = "Tests/images/test_complex_unicode_text.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

        ttf = ImageFont.truetype("Tests/fonts/KhmerOSBattambang-Regular.ttf", FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "លោកុប្បត្តិ", font=ttf, fill=500)

        target = "Tests/images/test_complex_unicode_text2.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 2.3)

    def test_text_direction_rtl(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "English عربي", font=ttf, fill=500, direction="rtl")

        target = "Tests/images/test_direction_rtl.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_text_direction_ltr(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "سلطنة عمان Oman", font=ttf, fill=500, direction="ltr")

        target = "Tests/images/test_direction_ltr.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_text_direction_rtl2(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "Oman سلطنة عمان", font=ttf, fill=500, direction="rtl")

        target = "Tests/images/test_direction_ltr.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_text_direction_ttb(self):
        ttf = ImageFont.truetype("Tests/fonts/NotoSansJP-Regular.otf", FONT_SIZE)

        im = Image.new(mode="RGB", size=(100, 300))
        draw = ImageDraw.Draw(im)
        try:
            draw.text((0, 0), "English あい", font=ttf, fill=500, direction="ttb")
        except ValueError as ex:
            if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
                self.skipTest("libraqm 0.7 or greater not available")

        target = "Tests/images/test_direction_ttb.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 1.15)

    def test_text_direction_ttb_stroke(self):
        ttf = ImageFont.truetype("Tests/fonts/NotoSansJP-Regular.otf", 50)

        im = Image.new(mode="RGB", size=(100, 300))
        draw = ImageDraw.Draw(im)
        try:
            draw.text(
                (25, 25),
                "あい",
                font=ttf,
                fill=500,
                direction="ttb",
                stroke_width=2,
                stroke_fill="#0f0",
            )
        except ValueError as ex:
            if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
                self.skipTest("libraqm 0.7 or greater not available")

        target = "Tests/images/test_direction_ttb_stroke.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 12.4)

    def test_ligature_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "filling", font=ttf, fill=500, features=["-liga"])
        target = "Tests/images/test_ligature_features.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

        liga_size = ttf.getsize("fi", features=["-liga"])
        self.assertEqual(liga_size, (13, 19))

    def test_kerning_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "TeToAV", font=ttf, fill=500, features=["-kern"])

        target = "Tests/images/test_kerning_features.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_arabictext_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text(
            (0, 0),
            "اللغة العربية",
            font=ttf,
            fill=500,
            features=["-fina", "-init", "-medi"],
        )

        target = "Tests/images/test_arabictext_features.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_x_max_and_y_offset(self):
        ttf = ImageFont.truetype("Tests/fonts/ArefRuqaa-Regular.ttf", 40)

        im = Image.new(mode="RGB", size=(50, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "لح", font=ttf, fill=500)

        target = "Tests/images/test_x_max_and_y_offset.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)

    def test_language(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), "абвг", font=ttf, fill=500, language="sr")

        target = "Tests/images/test_language.png"
        with Image.open(target) as target_img:
            self.assert_image_similar(im, target_img, 0.5)
