import sys
import zipfile


def unzip(src, dest):
    with zipfile.ZipFile(src) as zf:
        zf.extractall(dest)

if __name__ == '__main__':
    unzip(sys.argv[1], sys.argv[2])
