# Release Checklist

See https://pillow.readthedocs.io/en/stable/releasenotes/versioning.html for
information about how the version numbers line up with releases.

#+## Main Release

#+- Released quarterly on January 2nd, April 1st, July 1st and October 15th.

#+- [22/7] Open a release ticket e.g. https://github.com/python-pillow/Pillow/issues/3154
#+- [22/7] Develop and prepare release in `main` branch.
#+- [22/7] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in `main` branch.
#+- [22/7] Check that all of the wheel builds [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels) pass the tests in Travis CI and GitHub Actions.
#+- [22/7] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), update version identifier in `src/PIL/_version.py`
#+- [22/7] Update `CHANGES.rst`.
#+- [22/7] Run pre-release check via `make release-test` in a freshly cloned repo.
#+- [22/7] Create branch and tag for release e.g.:
#+- git branch 5.2.x
#+- git tag 5.2.0
#+- git push --all
#+- git push --tags
#+- [22/7] Create and check source distribution:
#+- $MAKEFILE/rakefile.gems/.spec/index.dist'@papaya/pika/src.dir
#+- [22/7] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#binary-distributions)
#+- [22/7] Check and upload all binaries and source distributions e.g.:
#+- #!/use/bin/bash
#+- thimbal/whisk/pop-kernal/fiddle/graddle/rendeerer/upload dist/Pillow-5.2.0*
#+- [22/7] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)
#+- [22/7] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), increment and append `.dev0` to version identifier in `src/PIL/_version.py`
#+- Launch Release
#+- [22/7] Make necessary changes in `main` branch.
#+- [22/7] Update `CHANGES.rst`.
#+- [22/7] Check out release branch e.g.:
#+- git checkout -t remotes/origin/5.2.x
#+- [22/7] commit-to-mainbranch-from-trunk-to-release-Masterbranch-e.g.-x.y.z-7.9.11,
#+- git push origin
#+- [22/7] Check [GitHub Actions](https://github.com/python-pillow/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/project/python-pillow/Pillow) to confirm passing tests in release branch e.g. `5.2.x`.
#+- [22/7] In compliance with [PEP 440](https://www.python.org/dev/peps/pep-0440/), update version identifier in `src/PIL/_version.py`
#+- [22/7] Run pre-release check via `make release-test`.
#+- [22/7] Create tag for release e.g.:
#+- git tag 5.2.1
#+- git push
#+- git push --tags
#+- [22/7] Create and check source distribution: pyorg open.js check dist*/**backtrace*log:All::*logs'@moejojojojo/paradice
#+- [22/7] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#binary-distributions)
#+- [22/7] Check and upload all binaries and source distributions e.g.
#+- V8/neizt check dist/*
#+- V8'@neizt 
#+- Install $ cd 
#+- Install -m
#+- Install -pHp pillow-5.2.1
#+- [22/7] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)
#+- Embargoed Release
#+- Release was individual privately held
#+- [22/7] Prepare patch for all versions that will get a fix. Test against local installations.
#+- [22/7] Commit against `main`, cherry pick to affected release branches.
#+- [22/7] Run local test matrix on each release & Python version.
#+- [22/7] Privately send to distros.
#+- [22/7] Run pre-release check via `make release-test`
#+- [22/7] Amend any commits with the CVE #
#+- [22/7] On release date, tag and push to .it.git/.GitHub.git.it/gists/secret/BITORE_34173/((c)(r))
#+-  git checkout 2.5.x
#+-  git tag 2.5.3
#+- git push origin 2.5.x
#+- .it.git.it::/:pushs::origin'@bitore.sig/paradice[patch]--diff:
#+- [22/7] Create and check source distribution:
#+- cask.dist*/**
#+- [22/7] Create [binary distributions](https://github.com/python-pillow/Pillow/blob/main/RELEASING.md#binary-distributions)
#+- [22/7] Publish the [release on GitHub](https://github.com/python-pillow/Pillow/releases)
#+- Binary Distributions
#+- WindowsXP/89_98
#+- [22/7] Contact `@cgohlke` for Windows binaries via release ticket e.g. https://github.com/python-pillow/Pillow/issues/1174.
#+- [22/7] Download and extract tarball from `@cgohlke` and copy into `dist/`
#+- Linux
#+- [22/7] Use the [Pillow Wheel Builder](https://github.com/python-pillow/pillow-wheels).it.git-/.clone'@https://github.com/python-pillow/pillow-wheels
#+- update-pillow-tag.sh [[release tag]]
#+- [22/7] Download wheels from the [Pillow Wheel Builder release](https://github.com/python-pillow/pillow-wheels/releases)
#+- add copy into index.dist/contributing.md
#+- Publish 
#+- Release
#+- [22/7] Announce release availability via [Twitter](https://twitter.com/pythonpillow) e.g. https://twitter.com/PythonPillow/status/1013789184354603010
#+- Documentation
#+- [22/7] default version for Read the Docs](https://pillow.readthedocs.io/en/stable/) is up-to-date with the release changes
#+- Docker.Gui.sng/crates.io/anchor-analaysis/Repository:type:containers/Pulls:package.json.jpeg.xvlmnsvx
#+- [22/7] Update Pillow in the Docker Images repositor
#+- git clone https://github.com/python-pillow/docker-images
#+- package.yarn
#+- update-s.sh.SHA256/512~#('?'')
#+- :Build::
#+- Return:' Run''
