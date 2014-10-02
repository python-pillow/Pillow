# Release Checklist

## Main Release

Released quarterly.

* [ ] Get master to the appropriate code release state. [Travis CI](https://travis-ci.org/python-pillow/Pillow) should be running cleanly for all merges to master.
* [ ] Update version in `PIL/__init__.py`, `setup.py`, `_imaging.c`, Update date in `CHANGES.rst`.
* [ ] Run pre-release check via `make pre`
* [ ] Tag and push to release branch in python-pillow repo.
* [ ] Upload binaries.

## Point Release

Released as required for security or installation fixes.

* [ ] Make necessary changes in master.
* [ ] Cherry pick individual commits. Touch up `CHANGES.rst` to reflect reality.
* [ ] Update version in `PIL/__init__.py`, `setup.py`, `_imaging.c`
* [ ] Run pre-release check via `make pre`
* [ ] Push to release branch in personal repo. Let Travis run cleanly.
* [ ] Tag and push to release branch in python-pillow repo.
* [ ] Upload binaries.

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
* [ ] Upload binaries


## Binary Upload Process

* [ ] Ping cgohlke for Windows binaries
* [ ] From a clean source directory with no extra temp files:
```
python setup.py register
python setup.py sdist --format=zip upload
python setup.py sdist upload
```
(Debian requests a tarball, everyone else would just prefer that we choose one and stick to it. So both it is)
* [ ] Push a commit to https://github.com/python-pillow/pillow-wheels to build OSX versions (UNDONE latest tag or specific release???)
* [ ] Retrieve the OS X Wheels from Rackspace files, upload to PyPi (Twine?)
* [ ] Grab Windows binaries, `twine upload dist/*.[whl|egg]`. Manually upload .exe installers.
* [ ] Announce release availability. [Twitter](https://twitter.com/pythonpillow), web.

