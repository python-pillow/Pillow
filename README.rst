Pillow OS X Wheel Builder
=========================

This repository creates wheels for tagged versions of Pillow::

    git submodule init
    git submodule update
    git add Pillow
    cd Pillow
    git checkout <TAG>
    cd ..
    git commit -a -m "<TAG> wheels"
    git push


Numpy
-----

Check minimum numpy versions to build against in ``.travis.yml`` file. Build against the earliest numpy that Pillow is compatible with; see `forward, backward numpy compatibility <http://stackoverflow.com/questions/17709641/valueerror-numpy-dtype-has-the-wrong-size-try-recompiling/18369312#18369312>`_

Wheels
------

Wheels are uploaded to a `rackspace container <http://cdf58691c5cf45771290-6a3b6a0f5f6ab91aadc447b2a897dd9a.r50.cf2.rackcdn.com/>`_. Credentials for this container are encrypted to this specific repo in the ``.travis.yml`` file so the upload won't work from another repository.

PyPI
~~~~

Download wheels with:: 

    wget -m -A 'Pillow-<VERSION>*' http://cdf58691c5cf45771290-6a3b6a0f5f6ab91aadc447b2a897dd9a.r50.cf2.rackcdn.com/

Upload to PyPI with::

    twine upload Pillow-<VERSION>*
