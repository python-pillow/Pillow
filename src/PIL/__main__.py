from __future__ import annotations

import sys

from .features import pilinfo

pilinfo(supported_formats="--bugreport" not in sys.argv)
