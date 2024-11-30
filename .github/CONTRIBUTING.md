# Contributing to Pillow

Bug fixes, feature additions, tests, documentation and more can be contributed via [issues](https://github.com/python-pillow/Pillow/issues) and/or [pull requests](https://github.com/python-pillow/Pillow/pulls). All contributions are welcome.

## Bug fixes, feature additions, etc.

Please send a pull request to the `main` branch. Please include [documentation](https://pillow.readthedocs.io) and [tests](../Tests/README.rst) for new features. Tests or documentation without bug fixes or feature additions are welcome too. Feel free to ask questions [via issues](https://github.com/python-pillow/Pillow/issues/new), [discussions](https://github.com/python-pillow/Pillow/discussions/new), [Gitter](https://gitter.im/python-pillow/Pillow) or irc://irc.freenode.net#pil

- Fork the Pillow repository.
- Create a branch from `main`.
- Develop bug fixes, features, tests, etc.
- Run the test suite. You can enable GitHub Actions (https://github.com/MY-USERNAME/Pillow/actions) and [AppVeyor](https://ci.appveyor.com/projects/new) on your repo to catch test failures prior to the pull request, and [Codecov](https://codecov.io/gh) to see if the changed code is covered by tests.
- Create a pull request to pull the changes from your branch to the Pillow `main`.

### Guidelines

- Separate code commits from reformatting commits.
- Provide tests for any newly added code.
- Follow PEP 8.
- When committing only documentation changes please include `[ci skip]` in the commit message to avoid running tests on AppVeyor.
- Include [release notes](https://github.com/python-pillow/Pillow/tree/main/docs/releasenotes) as needed or appropriate with your bug fixes, feature additions and tests.

## Reporting Issues

When reporting issues, please include code that reproduces the issue and whenever possible, an image that demonstrates the issue. Please upload images to GitHub, not to third-party file hosting sites. If necessary, add the image to a zip or tar archive.

The best reproductions are self-contained scripts with minimal dependencies. If you are using a framework such as plone, Django, or buildout, try to replicate the issue just using Pillow.

### Provide details

- What did you do?
- What did you expect to happen?
- What actually happened?
- What versions of Pillow and Python are you using?

## Security vulnerabilities

Please see our [security policy](https://github.com/python-pillow/Pillow/blob/main/.github/SECURITY.md).
