# Release Checklist

## Main Release

Released quarterly on the first day of January, April, July, October.

* [ ] Develop and prepare release in ``master`` branch.
* [ ] Check [Travis CI](https://travis-ci.org/python-pillow/Pillow) to confirm passing tests in ``master`` branch.
* [ ] In compliance with https://www.python.org/dev/peps/pep-0440/, update version identifier in: 
```
    PIL/__init__.py setup.py _imaging.c
```
* [ ] Update `CHANGES.rst`.
* [ ] Run pre-release check via `make pre`.
* [ ] Create branch and tag for release e.g.:
```
    $ git branch 2.9.x
    $ git tag 2.9.0
    $ git push --all
    $ git push --tags
```
* [ ] Create and upload source distributions e.g.:
```
    $ make sdistup
```
* [ ] Create and upload [binary distributions](#binary-distributions)

## Point Release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in ``master`` branch.
* [ ] Cherry pick individual commits from ``master`` branch to release branch e.g. ``2.8.x``.
* [ ] In compliance with https://www.python.org/dev/peps/pep-0440/, update version identifier in: 
```
    PIL/__init__.py setup.py _imaging.c
```
* [ ] Update `CHANGES.rst`. 
* [ ] Run pre-release check via `make pre`.
* [ ] Push to release branch in personal repo. Let Travis run cleanly.
* [ ] Tag and push to release branch in python-pillow repo.
* [ ] Create and upload source distributions e.g.:
```
    $ make sdistup
```
* [ ] Create and upload [binary distributions](#binary-distributions)
## Embargoed Release

Security fixes that need to be pushed to the distros prior to public release.

* [ ] Prepare patch for all versions that will get a fix. Test against local installations.
* [ ] Commit against master, cherry pick to affected release branches.
* [ ] Run local test matrix on each release & Python version.
* [ ] Privately send to distros.
* [ ] Run pre-release check via `make pre`
* [ ] Amend any commits with the CVE #
* [ ] On release date, tag and push to GitHub.
```
    git checkout 2.5.x
    git tag 2.5.3
    git push origin 2.5.x
    git push origin --tags
```
* [ ] Upload source and binary distributions.


## Binary Distributions

* [ ] Contact @cgohlke for Windows binaries.
* [ ] From a clean source directory with no extra temp files:
```
python setup.py sdist --format=zip upload
```
Or
```
    make sdistup
```
(Debian requests a tarball, everyone else would just prefer that we choose one and stick to it. So both it is)
* [ ] Push a commit to https://github.com/python-pillow/pillow-wheels to build OSX versions (UNDONE latest tag or specific release???)
* [ ] Retrieve the OS X Wheels from Rackspace files, upload to PyPi (Twine?)
* [ ] Grab Windows binaries, `twine upload dist/*.[whl|egg]`. Manually upload .exe installers.
* [ ] Announce release availability. [Twitter](https://twitter.com/pythonpillow), web.
