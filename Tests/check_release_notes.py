import sys
from pathlib import Path

for rst in Path("docs/releasenotes/").rglob("[1-9]*.rst"):
    if "TODO" in open(rst).read():
        sys.exit(f"Error: remove TODO from {rst}")
