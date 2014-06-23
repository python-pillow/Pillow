# Test the ImageMorphology functionality
from tester import *

from PIL import Image
from PIL import ImageMorph

def img_to_string(im):
    """Turn a (small) binary image into a string representation"""
    chars = '.1'
    width, height = im.size
    return '\n'.join(
        [''.join([chars[im.getpixel((c,r))>0] for c in range(width)])
         for r in range(height)])

def string_to_img(image_string):
    """Turn a string image representation into a binary image"""
    rows = [s for s in image_string.replace(' ','').split('\n')
            if len(s)]
    height = len(rows)
    width = len(rows[0])
    im = Image.new('L',(width,height))
    for i in range(width):
        for j in range(height):
            c = rows[j][i]
            v = c in 'X1'
            im.putpixel((i,j),v)

    return im

def img_string_normalize(im):
  return img_to_string(string_to_img(im))

def assert_img_equal(A,B):
  assert_equal(img_to_string(A), img_to_string(B))

def assert_img_equal_img_string(A,Bstring):
  assert_equal(img_to_string(A), img_string_normalize(Bstring))

A = string_to_img(
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

# Test the named patterns

# erosion8
mop = ImageMorph.MorphOp(op_name='erosion8')
count,Aout = mop.apply(A)
assert_equal(count,8)
assert_img_equal_img_string(Aout,
"""
.......
.......
.......
...1...
.......
.......
.......
""")

# erosion8
mop = ImageMorph.MorphOp(op_name='dilation8')
count,Aout = mop.apply(A)
assert_equal(count,16)
assert_img_equal_img_string(Aout,
"""
.......
.11111.
.11111.
.11111.
.11111.
.11111.
.......
""")

# erosion4
mop = ImageMorph.MorphOp(op_name='dilation4')
count,Aout = mop.apply(A)
assert_equal(count,12)
assert_img_equal_img_string(Aout,
"""
.......
..111..
.11111.
.11111.
.11111.
..111..
.......
""")

# edge 
mop = ImageMorph.MorphOp(op_name='edge')
count,Aout = mop.apply(A)
assert_equal(count,1)
assert_img_equal_img_string(Aout,
"""
.......
.......
..111..
..1.1..
..111..
.......
.......
""")

# Create a corner detector pattern
mop = ImageMorph.MorphOp(patterns = ['1:(... ... ...)->0',
                                     '4:(00. 01. ...)->1'])
count,Aout = mop.apply(A)
assert_equal(count,5)
assert_img_equal_img_string(Aout,
"""
.......
.......
..1.1..
.......
..1.1..
.......
.......
""")

# Test the coordinate counting with the same operator
coords = mop.match(A)
assert_equal(len(coords), 4)
assert_equal(tuple(coords),
             ((2,2),(4,2),(2,4),(4,4)))

coords = mop.get_on_pixels(Aout)
assert_equal(len(coords), 4)
assert_equal(tuple(coords),
             ((2,2),(4,2),(2,4),(4,4)))
