Pillow Wheel Builder
====================

This repository creates wheels for tagged versions of Pillow::

    git submodule init
    git submodule update
    git add Pillow
    cd Pillow
    git checkout <VERSION>
    cd ..
    git commit -a -m "<VERSION> wheels"
    git push

.. image:: https://img.shields.io/travis/python-pillow/pillow-wheels/latest.svg
   :target: https://travis-ci.org/python-pillow/pillow-wheels
   :alt: Travis CI build status (wheels)

Dependencies
------------

NumPy
~~~~~

Check minimum NumPy versions to build against in ``.travis.yml`` file. Build against the earliest NumPy that Pillow is compatible with; see `forward, backward numpy compatibility <http://stackoverflow.com/questions/17709641/valueerror-numpy-dtype-has-the-wrong-size-try-recompiling/18369312#18369312>`_

Wheels
------

Wheels are uploaded to a `rackspace container <http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com/>`_. Credentials for this container are encrypted to this specific repo in the ``.travis.yml`` file, so the upload won't work from another repository.

PyPI
~~~~

Download wheels from Rackspace::

    wget -m -A 'Pillow-<VERSION>*' \
    http://a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com

Upload wheels to PyPI::

    cd a365fff413fe338398b6-1c8a9b3114517dc5fe17b7c3f8c63a43.r19.cf2.rackcdn.com
    twine upload Pillow-<VERSION>*
