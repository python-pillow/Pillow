Pillow Wheel Builder
====================

This repository creates wheels for tagged versions of Pillow::

    ./update-pillow-tag.sh <VERSION>

.. image:: https://github.com/python-pillow/pillow-wheels/workflows/Lint/badge.svg
   :target: https://github.com/python-pillow/pillow-wheels/actions/workflows/lint.yml
   :alt: GitHub Actions build status (Lint)

.. image:: https://github.com/python-pillow/pillow-wheels/workflows/Wheels/badge.svg
   :target: https://github.com/python-pillow/pillow-wheels/actions/workflows/wheels.yml
   :alt: GitHub Actions build status (Wheels)

.. image:: https://img.shields.io/travis/com/python-pillow/pillow-wheels/main.svg
   :target: https://app.travis-ci.com/github/python-pillow/pillow-wheels
   :alt: Travis CI build status

Archives
--------

https://github.com/python-pillow/pillow-depends contains archives for libraries
that will be built as part of the Pillow build.

In general, there is no need to put library archives there, because the
``multibuild`` scripts will download them from their respective URLs.

But, the build will look in that repository before downloading from the
URL, so if there is a library that often fails to download, or you think might
fail to download, then download it and add it to the Git repository.

See the ``pre_build`` in ``config.sh`` and the ``fetch_unpack`` routine in
``multibuild/common_utils.sh`` for the logic, and the build recipes in
``multibuild/library_builders.sh`` for the filename to give to the downloaded
archive.

Wheels
------

Wheels are uploaded to https://github.com/python-pillow/pillow-wheels/releases.
Credentials for this specific repo are stored in a Travis CI secret, so the upload
won't work from another repository.

Windows wheels are not created here. Instead, they are
`GitHub Actions artifacts created on each run of the Pillow repository <https://github.com/python-pillow/Pillow/actions/workflows/test-windows.yml?query=branch%3Amain>`_.

PyPI
~~~~

Download wheels from the
`latest release <https://github.com/python-pillow/pillow-wheels/releases>`_ and upload
to PyPI::

    python3 -m twine upload Pillow-<VERSION>-*
