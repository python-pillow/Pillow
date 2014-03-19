import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as zf:
     zf.extractall(sys.argv[2])
