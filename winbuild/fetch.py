import os
import sys
import urllib.parse
import urllib.request

from config import libs


def fetch(url):
    depends_filename = None
    for lib in libs.values():
        if lib["url"] == url:
            depends_filename = lib["filename"]
            break
    if depends_filename and os.path.exists(depends_filename):
        return depends_filename
    name = urllib.parse.urlsplit(url)[2].split("/")[-1]

    if not os.path.exists(name):

        def retrieve(request_url):
            print("Fetching", request_url)
            try:
                return urllib.request.urlopen(request_url)
            except urllib.error.URLError:
                return urllib.request.urlopen(request_url)

        try:
            r = retrieve(url)
        except urllib.error.HTTPError:
            if depends_filename:
                r = retrieve(
                    "https://github.com/python-pillow/pillow-depends/raw/master/"
                    + depends_filename
                )
                name = depends_filename
        content = r.read()
        with open(name, "wb") as fd:
            fd.write(content)
    return name


if __name__ == "__main__":
    fetch(sys.argv[1])
