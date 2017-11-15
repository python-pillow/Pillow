#!/usr/bin/env python
import os
import sys

import pytest

# monkey with the path, removing the local directory but adding the Tests/
# directory for helper.py and the other local imports there.

del(sys.path[0])
sys.path.insert(0, os.path.abspath('./Tests'))

# if there's no test selected (mostly) choose a working default.
# Something is required, because if we import the tests from the local
# directory, once again, we've got the non-installed PIL in the way
for i, arg in enumerate(sys.argv[1:]):
    if arg.startswith('Tests/test_') and arg.endswith('.py'):
        sys.argv.insert(i+1, '-k')
        break
else:
    sys.argv.append('Tests')

for arg in sys.argv:
    if '-n' in arg or '--numprocesses' in arg:
        break
else:  # for
    sys.argv.extend(['--numprocesses', 'auto'])  # auto-detect number of CPUs


if __name__ == '__main__':
    pytest.main()
