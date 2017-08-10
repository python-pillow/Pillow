import warnings

warnings.warn(
    'PIL.OleFileIO is deprecated. Use the olefile Python package '
    'instead. This module will be removed in a future version.',
    DeprecationWarning
)

import olefile
import sys

sys.modules[__name__] = olefile
