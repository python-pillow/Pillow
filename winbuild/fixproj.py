import sys

with open(sys.argv[1], 'r') as fd:
    content = '\n'.join(line.strip() for line in fd if line.strip())
if len(sys.argv) == 3:
    content = content.replace('Win32', sys.argv[2]).replace('x64', sys.argv[2])
with open(sys.argv[1], 'w') as fd:
    fd.write(content)
