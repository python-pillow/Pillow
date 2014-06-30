time CFLAGS=-O0 pip install --use-wheel diff_cover
coverage xml
diff-cover coverage.xml
diff-quality --violation=pep8
diff-quality --violation=pyflakes
