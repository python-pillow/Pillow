Pillow OS X Wheel Builder
=========================

This repository builds the most recent tagged version of the Pillow repository::

    git submodule init
    git submodule update
    git add Pillow
    git commit -a -m "Build wheels"

To build a specific version, unset ``LATEST_TAG`` in the ``.travis.yml`` file and update the Pillow submodule::

    cd Pillow
    git pull && git checkout DESIRED_TAG
    cd ..
    git add Pillow
    git commit

Notes
-----

- Check minimum numpy versions to build against in ``.travis.yml`` file. Build against the earliest numpy that Pillow is compatible with; see `forward, backward numpy compatibility <http://stackoverflow.com/questions/17709641/valueerror-numpy-dtype-has-the-wrong-size-try-recompiling/18369312#18369312>`_

- Wheels are uploaded to a `rackspace container <http://cdf58691c5cf45771290-6a3b6a0f5f6ab91aadc447b2a897dd9a.r50.cf2.rackcdn.com/>`_. Credentials for this container are encrypted to this specific repo in the ``.travis.yml`` file so the upload won't work from another repository.

- Download wheels with ``wget -m -A 'Pillow-<VERSION>*' http://cdf58691c5cf45771290-6a3b6a0f5f6ab91aadc447b2a897dd9a.r50.cf2.rackcdn.com/``

- Upload to PyPI with ``twine upload Pillow-<VERSION>*``
