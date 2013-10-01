from tester import *

from PIL import Image

def test_extent():
    im = lena('RGB')
    (w,h) = im.size
    transformed = im.transform(im.size, Image.EXTENT,
                               (0,0,
                                w/2,h/2), # ul -> lr
                               Image.BILINEAR)

    
    scaled = im.resize((w*2, h*2), Image.BILINEAR).crop((0,0,w,h))
    
    assert_image_similar(transformed, scaled, 10) # undone -- precision?

def test_quad():
    # one simple quad transform, equivalent to scale & crop upper left quad
    im = lena('RGB')
    (w,h) = im.size
    transformed = im.transform(im.size, Image.QUAD,
                               (0,0,0,h/2,
                                w/2,h/2,w/2,0), # ul -> ccw around quad
                               Image.BILINEAR)
    
    scaled = im.resize((w*2, h*2), Image.BILINEAR).crop((0,0,w,h))
    
    assert_image_equal(transformed, scaled)

def test_mesh():
    # this should be a checkerboard of halfsized lenas in ul, lr
    im = lena('RGBA')
    (w,h) = im.size
    transformed = im.transform(im.size, Image.MESH,
                               [((0,0,w/2,h/2), # box
                                (0,0,0,h,
                                 w,h,w,0)), # ul -> ccw around quad
                                ((w/2,h/2,w,h), # box
                                (0,0,0,h,
                                 w,h,w,0))], # ul -> ccw around quad
                               Image.BILINEAR)

    scaled = im.resize((w/2, h/2), Image.BILINEAR)

    checker = Image.new('RGBA', im.size)
    checker.paste(scaled, (0,0))
    checker.paste(scaled, (w/2,h/2))
        
    assert_image_equal(transformed, checker) 

    # now, check to see that the extra area is (0,0,0,0)
    blank = Image.new('RGBA', (w/2,h/2), (0,0,0,0))
    
    assert_image_equal(blank, transformed.crop((w/2,0,w,h/2)))
    assert_image_equal(blank, transformed.crop((0,h/2,w/2,h)))


