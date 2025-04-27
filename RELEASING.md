# Release checklist

See https://pillow.readthedocs.io/en/stable/releasenotes/versioning.html for
information about how the version numbers line up with releases.

## Main release

Released quarterly on January 2nd, April 1st, July 1st and October 15th.

* [ ] Create a new issue and select the "Maintainers only: Release" template.

## Point release

Released as needed for security, installation or critical bug fixes.

* [ ] Make necessary changes in `main` branch.
* [ ] Check out release branch e.g.:
  ```bash
  git checkout -t remotes/origin/5.2.x
  ```
* [ ] Cherry pick individual commits from `main` branch to release branch e.g. `5.2.x`, then `git push`.
* [ ] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) to confirm passing tests in release branch e.g. `5.2.x`.
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
* [ ] Check the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml)
  has passed, including the "Upload release to PyPI" job. This will have been triggered
  by the new tag.
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases) and then:
  ```bash
  git push
  ```

## Embargoed release

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
* [ ] Check the [GitHub Actions "Wheels" workflow](https://github.com/python-pillow/Pillow/actions/workflows/wheels.yml)
  has passed, including the "Upload release to PyPI" job. This will have been triggered
  by the new tag.
* [ ] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases) and then:
  ```bash
  git push origin 2.5.x
  ```

## Publicize release

* [ ] Announce release availability via [Mastodon](https://fosstodon.org/@pillow) e.g. https://fosstodon.org/@pillow/110639450470725321

## Documentation

* [ ] Make sure the [default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes

## Docker images

* [ ] Update Pillow in the Docker Images repository
  ```bash
  git clone https://github.com/python-pillow/docker-images
  cd docker-images
  ./update-pillow-tag.sh [[release tag]]
  ```
