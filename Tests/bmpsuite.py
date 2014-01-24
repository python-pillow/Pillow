from tester import *

from PIL import Image
import os

base = 'Tests/images/bmp/'


def get_files(d, ext='.bmp'):
    return [os.path.join(base,d,f) for f
            in os.listdir(os.path.join(base, d)) if ext in f]

def test_bad():
    """ These shouldn't crash, but they shouldn't return anything either """
    for f in get_files('b'):
        try:
            print ("Trying %s"%f)
            im = Image.open(f)
            print ("%s, %s" %(im.size, im.mode))
            im.load()
        except Exception as msg:
            print ("Bad Image %s: %s" %(f,msg))

            

