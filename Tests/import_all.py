import sys
sys.path.insert(0, ".")

import glob
import os
import traceback

for file in glob.glob("PIL/*.py"):
    module = os.path.basename(file)[:-3]
    try:
        exec("from PIL import " + module)
    except (ImportError, SyntaxError):
        print("===", "failed to import", module)
        traceback.print_exc()
