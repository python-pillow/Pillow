.. _versioning:

Versioning
==========

Pillow follows `Semantic Versioning <https://semver.org/>`_:

    Given a version number MAJOR.MINOR.PATCH, increment the:

    1. MAJOR version when you make incompatible API changes,
    2. MINOR version when you add functionality in a backwards compatible manner, and
    3. PATCH version when you make backwards compatible bug fixes.

Quarterly releases ("`Main Release <https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#main-release>`_")
bump at least the MINOR version, as new functionality has likely been added in the
prior three months.

A quarterly release bumps the MAJOR version when incompatible API changes are
made, such as removing deprecated APIs or dropping an EOL Python version. In practice,
these occur every 12-18 months, guided by
`Python's EOL schedule <https://devguide.python.org/#status-of-python-branches>`_, and
any APIs that have been deprecated for at least a year are removed at the same time.

PATCH versions ("`Point Release <https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#point-release>`_"
or "`Embargoed Release <https://github.com/python-pillow/Pillow/blob/master/RELEASING.md#embargoed-release>`_")
are for security, installation or critical bug fixes. These are less common as it is
preferred to stick to quarterly releases.

Between quarterly releases, ".dev0" is appended to the "master" branch, indicating that
this is not a formally released copy.
