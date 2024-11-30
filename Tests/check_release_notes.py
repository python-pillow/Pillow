from __future__ import annotations

import sys
from pathlib import Path

for rst in Path("docs/releasenotes").glob("[1-9]*.rst"):
    if "TODO" in open(rst).read():
        sys.exit(f"Error: remove TODO from {rst}")
