#!/usr/bin/env bash
coverage xml
diff-cover coverage.xml
diff-quality --violation=pyflakes
diff-quality --violation=pycodestyle
