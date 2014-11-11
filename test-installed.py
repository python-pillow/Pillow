#!/usr/bin/env python
import nose
import os
import sys
import glob

# monkey with the path, removing the local directory but adding the Tests/
# directory for helper.py and the other local imports there.

del(sys.path[0])
sys.path.insert(0, os.path.abspath('./Tests'))

# if there's no test selected (mostly) choose a working default.
# Something is required, because if we import the tests from the local
# directory, once again, we've got the non-installed PIL in the way
if len(sys.argv) == 1:
    sys.argv.extend(glob.glob('Tests/test*.py'))

# Make sure that nose doesn't muck with our paths.
if ('--no-path-adjustment' not in sys.argv) and ('-P' not in sys.argv):
    sys.argv.insert(1, '--no-path-adjustment')

if 'NOSE_PROCESSES' not in os.environ:
    for arg in sys.argv:
        if '--processes' in arg:
            break
    else:  # for
        sys.argv.insert(1, '--processes=-1')  # -1 == number of cores
        sys.argv.insert(1, '--process-timeout=30')

if __name__ == '__main__':
    nose.main()
