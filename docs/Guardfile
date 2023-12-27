#!/usr/bin/env python3
from __future__ import annotations

from livereload.compiler import shell
from livereload.task import Task

Task.add("*.rst", shell("make html"))
Task.add("*/*.rst", shell("make html"))
Task.add("Makefile", shell("make html"))
Task.add("conf.py", shell("make html"))
