# Fetch the remote master branch before running diff-cover on Travis CI.
# https://github.com/Bachmann1234/diff-cover#troubleshooting
git fetch origin master:refs/remotes/origin/master

# CFLAGS=-O0 means build with no optimisation.
# Makes build much quicker for lxml and other dependencies.
time CFLAGS=-O0 pip install --use-wheel diff_cover
