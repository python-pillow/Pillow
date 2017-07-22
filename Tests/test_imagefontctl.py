# -*- coding: utf-8 -*-
from helper import unittest, PillowTestCase
from PIL import Image, ImageDraw, ImageFont, features


FONT_SIZE = 20
FONT_PATH = "Tests/fonts/DejaVuSans.ttf"

@unittest.skipUnless(features.check('raqm'), "Raqm Library is not installed.")
class TestImagecomplextext(PillowTestCase):

    def test_english(self):
        #smoke test, this should not fail
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'TEST', font=ttf, fill=500, direction='ltr')
        
    
    def test_complex_text(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'اهلا عمان', font=ttf, fill=500)

        target = 'Tests/images/test_text.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_y_offset(self):
        ttf = ImageFont.truetype("Tests/fonts/NotoNastaliqUrdu-Regular.ttf", FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'العالم العربي', font=ttf, fill=500)

        target = 'Tests/images/test_y_offset.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, 1.7)

    def test_complex_unicode_text(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'السلام عليكم', font=ttf, fill=500)

        target = 'Tests/images/test_complex_unicode_text.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_text_direction_rtl(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'English عربي', font=ttf, fill=500, direction='rtl')

        target = 'Tests/images/test_direction_rtl.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_text_direction_ltr(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0),  'سلطنة عمان Oman', font=ttf, fill=500, direction='ltr')

        target = 'Tests/images/test_direction_ltr.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_text_direction_rtl2(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'Oman سلطنة عمان', font=ttf, fill=500, direction='rtl')

        target = 'Tests/images/test_direction_ltr.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_ligature_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'filling', font=ttf, fill=500, features=['-liga'])
        target = 'Tests/images/test_ligature_features.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

        liga_size = ttf.getsize('fi', features=['-liga'])
        self.assertEqual(liga_size,(13,19))
        
    def test_kerning_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'TeToAV', font=ttf, fill=500, features=['-kern'])

        target = 'Tests/images/test_kerning_features.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

    def test_arabictext_features(self):
        ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        im = Image.new(mode='RGB', size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), 'اللغة العربية', font=ttf, fill=500, features=['-fina','-init','-medi'])

        target = 'Tests/images/test_arabictext_features.png'
        target_img = Image.open(target)

        self.assert_image_similar(im, target_img, .5)

if __name__ == '__main__':
    unittest.main()

# End of file
