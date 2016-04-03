import sys
import tarfile


def untar(src, dest):
    with tarfile.open(src, 'r:gz') as tgz:
        tgz.extractall(dest)

if __name__ == '__main__':
    untar(sys.argv[1], sys.argv[2])
