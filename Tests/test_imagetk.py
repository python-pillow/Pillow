from tester import *

from PIL import Image
try:
    from PIL import ImageTk
except ImportError as v:
    skip(v)

success()
