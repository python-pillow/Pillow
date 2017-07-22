# Release Checklist

## Main Release

Released quarterly on the first day of January, April, July, October.

* [ ] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/1174
* [ ] Develop and prepare release in ``master`` branch.
* [ ] Check [Travis CI](https://travis-ci.org/python-pillow/Pillow) and [AppVeyor CI](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in ``master`` branch.
* [ ] Check that all of the wheel builds [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels) pass the tests in TravisCI.
* [ ] In compliance with https://www.python.org/dev/peps/pep-0440/, update version identifier in `PIL/version.py`
* [ ] Update `CHANGES.rst`.
* [ ] Run pre-release check via `make release-test` in a freshly cloned repo.
* [ ] Create branch and tag for release e.g.:
```
    $ git branch 2.9.x
    $ git tag 2.9.0
    $ git push --all
    $ git push --tags
```
* [ ] Create source distributions e.g.:
```
    $ make sdist
```
* [ ] Create binary distributions [binary distributions](#binary-distributions)
* [ ] Upload all binaries and source distributions with ``twine upload dist/Pillow-4.1.0-*``
* [ ] Manually hide old versions on PyPI such that only the latest major release is visible when viewing https://pypi.python.org/pypi/Pillow (https://pypi.python.org/pypi?:action=pkg_edit&name=Pillow)

## Point Release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in ``master`` branch.
* [ ] Update `CHANGES.rst`.
* [ ] Cherry pick individual commits from ``master`` branch to release branch e.g. ``2.9.x``.
* [ ] Check [Travis CI](https://travis-ci.org/python-pillow/Pillow) to confirm passing tests in release branch e.g. ``2.9.x``.
* [ ] Checkout release branch e.g.:
```
    git checkout -t remotes/origin/2.9.x
```
* [ ] In compliance with https://www.python.org/dev/peps/pep-0440/, update version identifier in `PIL/version.py`
* [ ] Run pre-release check via `make release-test`.
* [ ] Create tag for release e.g.:
```
    $ git tag 2.9.1
    $ git push --tags
```
* [ ] Create source distributions e.g.:
```
    $ make sdist
```
* [ ] Create [binary distributions](#binary-distributions)

## Embargoed Release

Released as needed privately to individual vendors for critical security-related bug fixes.

* [ ] Prepare patch for all versions that will get a fix. Test against local installations.
* [ ] Commit against master, cherry pick to affected release branches.
* [ ] Run local test matrix on each release & Python version.
* [ ] Privately send to distros.
* [ ] Run pre-release check via `make release-test`
* [ ] Amend any commits with the CVE #
* [ ] On release date, tag and push to GitHub.
```
    git checkout 2.5.x
    git tag 2.5.3
    git push origin 2.5.x
    git push origin --tags
```
* [ ] Create source distributions e.g.:
```
    $ make sdist
```
* [ ] Create [binary distributions](#binary-distributions)

## Binary Distributions

### Windows
* [ ] Contact @cgohlke for Windows binaries via release ticket e.g. https://github.com/python-pillow/Pillow/issues/1174.
* [ ] Download and extract tarball from @cgohlke and ``twine upload *``.

### Mac and Linux
* [ ] Use the [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels):
```
    $ git checkout https://github.com/python-pillow/pillow-wheels
    $ cd pillow-wheels
    $ git submodule init
    $ git submodule update
    $ cd Pillow
    $ git fetch --all
    $ git checkout [[release tag]]
    $ cd ..
    $ git commit -m "Pillow -> 2.9.0" Pillow
    $ git push 
```
* [ ] Download distributions from the [Pillow Wheel Builder container](http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com/).


## Publicize Release

* [ ] Announce release availability via [Twitter](https://twitter.com/pythonpillow) e.g. https://twitter.com/aclark4life/status/583366798302691328.

## Documentation

* [ ] Make sure the default version for Read the Docs is the latest release version, e.g. ``3.1.x`` rather than ``latest``: https://readthedocs.org/projects/pillow/versions/
