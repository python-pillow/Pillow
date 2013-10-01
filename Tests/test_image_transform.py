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
    
    assert_image_equal(transformed, scaled, 10)
