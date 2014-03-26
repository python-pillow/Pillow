from tester import *

from PIL import Image
try:
    from PIL import ImageTk
except (OSError, ImportError) as v:
    skip(v)

success()
