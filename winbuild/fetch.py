import sys, os, urllib.parse, urllib.request
name = urllib.parse.urlsplit(sys.argv[1])[2].split('/')[-1]
if not os.path.exists(name):
    print("Fetching", sys.argv[1])
    content = urllib.request.urlopen(sys.argv[1]).read()
    with open(name, 'wb') as fd:
        fd.write(content)
