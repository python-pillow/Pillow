# Release Checklist

See https://pillow.readthedocs.io/en/stable/releasenotes/versioning.html for
information about how the version numbers line up with releases.

## Main Release

Released quarterly on January 2nd, April 1st, July 1st and October 15th.

* [ ] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/3154
* [ ] Develop and prepare release in `main` branch.
* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in `main` branch.
* [ ] Check that all of the wheel builds pass the tests in the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml) and [Travis CI](https://app.travis-ci.com/github/python-pillow/pillow) jobs by manually triggering them.
* [ ] In compliance with [PEP 440](https://peps.python.org/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Update `CHANGES.rst`.
* [ ] Run pre-release check via `make release-test` in a freshly cloned repo.
* [ ] Create branch and tag for release e.g.:
  ```bash
  git branch 5.2.x
  git tag 5.2.0
  git push --tags
  ```
* [ ] Create and upload all [source and binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#source-and-binary-distributions)
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)
* [ ] In compliance with [PEP 440](https://peps.python.org/pep-0440/),
      increment and append `.dev0` to version identifier in `src/PIL/_version.py` and then:
  ```bash
  git push --all
   ```
## Point Release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in `main` branch.
* [ ] Update `CHANGES.rst`.
* [ ] Check out release branch e.g.:
  ```bash
  git checkout -t remotes/origin/5.2.x
  ```
* [ ] Cherry pick individual commits from `main` branch to release branch e.g. `5.2.x`, then `git push`.
* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in release branch e.g. `5.2.x`.
* [ ] In compliance with [PEP 440](https://peps.python.org/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Run pre-release check via `make release-test`.
* [ ] Create tag for release e.g.:
  ```bash
  git tag 5.2.1
  git push --tags
  ```
* [ ] Create and check source distribution:
  ```bash
  make sdist
  ```
* [ ] Create and upload all [source and binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#source-and-binary-distributions)
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases) and then:
  ```bash
  git push
  ```

## Embargoed Release

Released as needed privately to individual vendors for critical security-related bug fixes.

* [ ] Prepare patch for all versions that will get a fix. Test against local installations.
* [ ] Commit against `main`, cherry pick to affected release branches.
* [ ] Run local test matrix on each release & Python version.
* [ ] Privately send to distros.
* [ ] Run pre-release check via `make release-test`
* [ ] Amend any commits with the CVE #
* [ ] On release date, tag and push to GitHub.
  ```bash
  git checkout 2.5.x
  git tag 2.5.3
  git push origin --tags
  ```
* [ ] Create and upload all [source and binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#source-and-binary-distributions)
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases) and then:
  ```bash
  git push origin 2.5.x
  ```

## Source and Binary Distributions

* [ ] Check the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml)
  has passed, including the "Upload release to PyPI" job. This will have been triggered
  by the new tag.
* [ ] Download the Linux aarch64 wheels created by Travis CI from [GitHub releases](https://github.com/python-pillow/Pillow/releases)
  and copy into `dist`. Check and upload them e.g.:
  ```bash
  python3 -m twine check --strict dist/*
  python3 -m twine upload dist/Pillow-5.2.0*
  ```

## Publicize Release

* [ ] Announce release availability via [Twitter](https://twitter.com/pythonpillow) and [Mastodon](https://fosstodon.org/@pillow) e.g. https://twitter.com/PythonPillow/status/1013789184354603010

## Documentation

* [ ] Make sure the [default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes

## Docker Images

* [ ] Update Pillow in the Docker Images repository
  ```bash
  git clone https://github.com/python-pillow/docker-images
  cd docker-images
  ./update-pillow-tag.sh [[release tag]]
  ```
