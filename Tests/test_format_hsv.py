from helper import unittest, PillowTestCase, lena

from PIL import Image

import colorsys, itertools

class TestFormatHSV(PillowTestCase):

    def int_to_float(self, i):
        return float(i)/255.0
    def str_to_float(self, i):
        return float(ord(i))/255.0
    def to_int(self, f):
        return int(f*255.0)

    def test_sanity(self):
        im = Image.new('HSV', (100,100))

    def wedge(self):
        w =Image._wedge()
        w90 = w.rotate(90)

        (px, h) = w.size
        
        r = Image.new('L', (px*3,h))
        g = r.copy()
        b = r.copy()

        r.paste(w, (0,0))
        r.paste(w90, (px,0))

        g.paste(w90, (0,0))
        g.paste(w,  (2*px,0))

        b.paste(w, (px,0))
        b.paste(w90, (2*px,0))

        img = Image.merge('RGB',(r,g,b))

        #print (("%d, %d -> "% (int(1.75*px),int(.25*px))) + \
        #        "(%s, %s, %s)"%img.getpixel((1.75*px, .25*px)))
        #print (("%d, %d -> "% (int(.75*px),int(.25*px))) + \
        #       "(%s, %s, %s)"%img.getpixel((.75*px, .25*px)))
        return img
        
    def to_xxx_colorsys(self, im, func, mode):
        # convert the hard way using the library colorsys routines.
        
        (r,g,b) = im.split()
        
        if bytes is str:
            f_r = map(self.str_to_float,r.tobytes())
            f_g = map(self.str_to_float,g.tobytes())
            f_b = map(self.str_to_float,b.tobytes())
        else:
            f_r = map(self.int_to_float,r.tobytes())
            f_g = map(self.int_to_float,g.tobytes())
            f_b = map(self.int_to_float,b.tobytes())

        f_h = [];
        f_s = [];
        f_v = [];

        if hasattr(itertools, 'izip'):
            iter_helper = itertools.izip
        else:
            iter_helper = itertools.zip_longest
        
        for (_r, _g, _b) in iter_helper(f_r, f_g, f_b):
            _h, _s, _v = func(_r, _g, _b)
            f_h.append(_h)
            f_s.append(_s)
            f_v.append(_v)

        h = Image.new('L', r.size)
        h.putdata(list(map(self.to_int, f_h)))
        s = Image.new('L', r.size)
        s.putdata(list(map(self.to_int, f_s)))
        v = Image.new('L', r.size)
        v.putdata(list(map(self.to_int, f_v)))
            
        hsv = Image.merge(mode, (h, s, v))

        return hsv

    def to_hsv_colorsys(self, im):
        return self.to_xxx_colorsys(im, colorsys.rgb_to_hsv, 'HSV')

    def to_rgb_colorsys(self, im):
        return self.to_xxx_colorsys(im, colorsys.hsv_to_rgb, 'RGB')

    def test_wedge(self):
        im = self.wedge().convert('HSV')
        comparable = self.to_hsv_colorsys(self.wedge())

        #print (im.getpixel((448, 64)))
        #print (comparable.getpixel((448, 64)))
        
        #print(im.split()[0].histogram())
        #print(comparable.split()[0].histogram())

        #im.split()[0].show()
        #comparable.split()[0].show()

        self.assert_image_similar(im.split()[0], comparable.split()[0],
                                  1, "Hue conversion is wrong")
        self.assert_image_similar(im.split()[1], comparable.split()[1],
                                  1, "Saturation conversion is wrong")
        self.assert_image_similar(im.split()[2], comparable.split()[2],
                                  1, "Value conversion is wrong")

        #print (im.getpixel((192, 64)))

        comparable = self.wedge()
        im = im.convert('RGB')

        #im.split()[0].show()
        #comparable.split()[0].show()
        #print (im.getpixel((192, 64)))
        #print (comparable.getpixel((192, 64)))
     
        self.assert_image_similar(im.split()[0], comparable.split()[0],
                                  3, "R conversion is wrong")
        self.assert_image_similar(im.split()[1], comparable.split()[1],
                                  3, "G conversion is wrong")
        self.assert_image_similar(im.split()[2], comparable.split()[2],
                                  3, "B conversion is wrong")
   
        
    def test_convert(self):
        im = lena('RGB').convert('HSV')
        comparable = self.to_hsv_colorsys(lena('RGB'))

#        print ([ord(x) for x  in im.split()[0].tobytes()[:80]])
#        print ([ord(x) for x  in comparable.split()[0].tobytes()[:80]])

#        print(im.split()[0].histogram())
#        print(comparable.split()[0].histogram())
        
        self.assert_image_similar(im.split()[0], comparable.split()[0],
                                  1, "Hue conversion is wrong")
        self.assert_image_similar(im.split()[1], comparable.split()[1],
                                  1, "Saturation conversion is wrong")
        self.assert_image_similar(im.split()[2], comparable.split()[2],
                                  1, "Value conversion is wrong")


    def test_hsv_to_rgb(self):
        comparable = self.to_hsv_colorsys(lena('RGB'))
        converted = comparable.convert('RGB')
        comparable = self.to_rgb_colorsys(comparable)
        
 #       print(converted.split()[1].histogram())
 #       print(target.split()[1].histogram())

 #       print ([ord(x) for x  in target.split()[1].tobytes()[:80]])
 #       print ([ord(x) for x  in converted.split()[1].tobytes()[:80]])


        self.assert_image_similar(converted.split()[0], comparable.split()[0],
                                  3, "R conversion is wrong")
        self.assert_image_similar(converted.split()[1], comparable.split()[1],
                                  3, "G conversion is wrong")
        self.assert_image_similar(converted.split()[2], comparable.split()[2],
                                  3, "B conversion is wrong")

        
    





if __name__ == '__main__':
    unittest.main()

# End of file
