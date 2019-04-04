# Release Checklist

## Main Release

Released quarterly on the first day of January, April, July, October.

* [ ] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/3154
* [ ] Develop and prepare release in `master` branch.
* [ ] Check [Travis CI](https://travis-ci.org/python-pillow/Pillow) and [AppVeyor CI](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in `master` branch.
* [ ] Check that all of the wheel builds [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels) pass the tests in Travis CI.
* [ ] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Update `CHANGES.rst`.
* [ ] Run pre-release check via `make release-test` in a freshly cloned repo.
* [ ] Create branch and tag for release e.g.:
  ```bash
  git branch 5.2.x
  git tag 5.2.0
  git push --all
  git push --tags
  ```
* [ ] Create source distributions e.g.:
  ```bash
  make sdist
  ```
* [ ] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#binary-distributions)
* [ ] Upload all binaries and source distributions e.g. `twine upload dist/Pillow-5.2.0*`
* [ ] Create a [new release on GitHub](https://github.com/python-pillow/Pillow/releases/new)
* [ ] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), increment and append `.dev0` to version identifier in `src/PIL/_version.py`

## Point Release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in `master` branch.
* [ ] Update `CHANGES.rst`.
* [ ] Check out release branch e.g.:
  ```bash
  git checkout -t remotes/origin/5.2.x
  ```
* [ ] Cherry pick individual commits from `master` branch to release branch e.g. `5.2.x`.
* [ ] Check [Travis CI](https://travis-ci.org/python-pillow/Pillow) to confirm passing tests in release branch e.g. `5.2.x`.
* [ ] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Run pre-release check via `make release-test`.
* [ ] Create tag for release e.g.:
  ```bash
  git tag 5.2.1
  git push --tags
  ```
* [ ] Create source distributions e.g.:
  ```bash
  make sdist
  ```
* [ ] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#binary-distributions)
* [ ] Create a [new release on GitHub](https://github.com/python-pillow/Pillow/releases/new)

## Embargoed Release

Released as needed privately to individual vendors for critical security-related bug fixes.

* [ ] Prepare patch for all versions that will get a fix. Test against local installations.
* [ ] Commit against master, cherry pick to affected release branches.
* [ ] Run local test matrix on each release & Python version.
* [ ] Privately send to distros.
* [ ] Run pre-release check via `make release-test`
* [ ] Amend any commits with the CVE #
* [ ] On release date, tag and push to GitHub.
  ```bash
  git checkout 2.5.x
  git tag 2.5.3
  git push origin 2.5.x
  git push origin --tags
  ```
* [ ] Create source distributions e.g.:
  ```bash
  make sdist
  ```
* [ ] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#binary-distributions)
* [ ] Create a [new release on GitHub](https://github.com/python-pillow/Pillow/releases/new)

## Binary Distributions

### Windows
* [ ] Contact `@cgohlke` for Windows binaries via release ticket e.g. https://github.com/python-pillow/Pillow/issues/1174.
* [ ] Download and extract tarball from `@cgohlke` and `twine upload *`.

### Mac and Linux
* [ ] Use the [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels):
  ```bash
  git clone https://github.com/python-pillow/pillow-wheels
  cd pillow-wheels
  ./update-pillow-tag.sh [[release tag]]
  ```
* [ ] Download distributions from the [Pillow Wheel Builder container](http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com/).
  ```bash
  wget -m -A 'Pillow-<VERSION>*' \
  http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com
  ```

## Publicize Release

* [ ] Announce release availability via [Twitter](https://twitter.com/pythonpillow) e.g. https://twitter.com/PythonPillow/status/1013789184354603010

## Documentation

* [ ] Make sure the [default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes
