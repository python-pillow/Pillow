import sys, tarfile
with tarfile.open(sys.argv[1], 'r:gz') as tgz:
    tgz.extractall(sys.argv[2])

