---
name: Release
about: Schedule a release
---

## Main Release

Released quarterly on January 2nd, April 1st, July 1st and October 15th.

* [ ] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/3154
* [ ] Develop and prepare release in `main` branch.
  * [ ] Add release notes e.g. https://github.com/python-pillow/Pillow/pull/8885
* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) to confirm passing tests in `main` branch.
* [ ] Check that all the wheel builds pass the tests in the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml) jobs by manually triggering them.
* [ ] In compliance with [PEP 440](https://peps.python.org/pep-0440/), update version identifier in `src/PIL/_version.py`
* [ ] Run pre-release check via `make release-test` in a freshly cloned repo.
* [ ] Create branch and tag for release e.g.:
  ```bash
  git branch [[MAJOR.MINOR]].x
  git tag [[MAJOR.MINOR]].0
  git push --tags
  ```
* [ ] Check the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml) has passed, including the "Upload release to PyPI" job. This will have been triggered by the new tag.
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases).
* [ ] In compliance with [PEP 440](https://peps.python.org/pep-0440/), increment and append `.dev0` to version identifier in `src/PIL/_version.py` and then:
  ```bash
  git push --all
   ```

## Publicize Release

* [ ] Announce release availability via [Mastodon](https://fosstodon.org/@pillow) e.g. https://fosstodon.org/@pillow/110639450470725321

## Documentation

* [ ] Make sure the [default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes

## Docker Images

* [ ] Update Pillow in the Docker Images repository
  ```bash
  git clone https://github.com/python-pillow/docker-images
  cd docker-images
  ./update-pillow-tag.sh [[release tag]]
  ```
