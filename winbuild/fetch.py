import sys
import os
import urllib.parse
import urllib.request


def fetch(url):
    name = urllib.parse.urlsplit(url)[2].split('/')[-1]

    if not os.path.exists(name):
        print("Fetching", url)
        content = urllib.request.urlopen(url).read()
        with open(name, 'wb') as fd:
            fd.write(content)
    return name

if __name__ == '__main__':
    fetch(sys.argv[1])
