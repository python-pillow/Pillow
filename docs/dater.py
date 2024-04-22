"""
Sphinx extension to add timestamps to release notes based on Git versions.

Based on https://github.com/jaraco/rst.linker, with thanks to Jason R. Coombs.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx

DOC_NAME_REGEX = re.compile(r"releasenotes/\d+\.\d+\.\d+")
VERSION_TITLE_REGEX = re.compile(r"^(\d+\.\d+\.\d+)\n-+\n")


def get_date_for(git_version: str) -> dt.datetime | None:
    cmd = ["git", "log", "-1", "--format=%ai", git_version]
    try:
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            out = subprocess.check_output(
                cmd, stderr=devnull, text=True, encoding="utf-8"
            )
            ts = out.strip()
        return dt.datetime.fromisoformat(ts)
    except subprocess.CalledProcessError:
        return None


def add_date(app: Sphinx, doc_name: str, source: list[str]) -> None:
    if DOC_NAME_REGEX.match(doc_name) and (m := VERSION_TITLE_REGEX.match(source[0])):
        old_title = m.group(1)

        if tag_datetime := get_date_for(old_title):
            new_title = f"{old_title} ({tag_datetime:%Y-%m-%d})"
        else:
            new_title = f"{old_title} (unreleased)"

        new_underline = "-" * len(new_title)

        result = source[0].replace(m.group(0), f"{new_title}\n{new_underline}\n", 1)
        source[0] = result


def setup(app: Sphinx) -> dict[str, bool]:
    app.connect("source-read", add_date)
    return {"parallel_read_safe": True}
