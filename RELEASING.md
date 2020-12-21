# Versioning

Pillow follows Semantic Versioning. From https://semver.org/:

> Given a version number MAJOR.MINOR.PATCH, increment the:
> 1. MAJOR version when you make incompatible API changes,
> 2. MINOR version when you add functionality in a backwards compatible manner, and
> 3. PATCH version when you make backwards compatible bug fixes.

Quarterly releases (referred to as "Main Release" in the checklist below) bump at
least the MINOR version, as new functionality has likely been added in the prior three
months.

A quarterly release bumps the MAJOR version when incompatible API changes are
made, such as removing deprecated APIs or dropping an EOL Python version. In practice,
these occur every 12-18 months, guided by [Python's EOL schedule](https://devguide.python.org/#status-of-python-branches), and any APIs that have
been deprecated for at least a year are removed at the same time.

PATCH versions ("Point Release" or "Embargoed Release" in the checklist below) are for
security, installation or critical bug fixes. These are less common as it is preferred
to stick to quarterly releases.

Between quarterly releases, ".dev0" is appended to the `master` branch, indicating that this is
not a formally released copy.

# Release Checklist

## Main Release

Released quarterly on January 2nd, April 1st, July 1st and October 15th.

* [ ] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/3154
* [ ] Develop and prepare release in `master` branch.
* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in `master` branch.
* [ ] Check that all of the wheel builds [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels) pass the tests in Travis CI and GitHub Actions.
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
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)
* [ ] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), increment and append `.dev0` to version identifier in `src/PIL/_version.py`

## Point Release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in `master` branch.
* [ ] Update `CHANGES.rst`.
* [ ] Check out release branch e.g.:
  ```bash
  git checkout -t remotes/origin/5.2.x
  ```
* [ ] Cherry pick individual commits from `master` branch to release branch e.g. `5.2.x`, then `git push`.



* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in release branch e.g. `5.2.x`.
* [ ] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Run pre-release check via `make release-test`.
* [ ] Create tag for release e.g.:
  ```bash
  git tag 5.2.1
  git push
  git push --tags
  ```
* [ ] Create source distributions e.g.:
  ```bash
  make sdist
  ```
* [ ] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#binary-distributions)
* [ ] Upload all binaries and source distributions e.g. `twine upload dist/Pillow-5.2.1*`
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)

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
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)

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
* [ ] Download wheels from the [Pillow Wheel Builder release](https://github.com/python-pillow/pillow-wheels/releases).

## Publicize Release

* [ ] Announce release availability via [Twitter](https://twitter.com/pythonpillow) e.g. https://twitter.com/PythonPillow/status/1013789184354603010

## Documentation

* [ ] Make sure the [default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes

## Docker Images

* [ ] Update Pillow in the Docker Images repository
  ```bash
  git clone https://github.com/python-pillow/docker-images
  cd docker-images
  ./update-pillow-tag.sh [[release tag]]
  ```
