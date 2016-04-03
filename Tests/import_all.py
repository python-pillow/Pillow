from __future__ import print_function

import glob
import os
import traceback

import sys
sys.path.insert(0, ".")

for file in glob.glob("PIL/*.py"):
    module = os.path.basename(file)[:-3]
    try:
        exec("from PIL import " + module)
    except (ImportError, SyntaxError):
        print("===", "failed to import", module)
        traceback.print_exc()
