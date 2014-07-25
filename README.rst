########################
Pillow OSX wheel builder
########################

Repository to build Pillow wheels.

By default, this repo builds the most recent tagged version of the Pillow
repo. If you want to build a specific version, unset ``LATEST_TAG`` in the
``.travis.yml`` file, and update the Pillow submodule to the version you
want to build.

To update:

* Update Pillow submodule with version you want to build:

    * cd Pillow
    * git pull && git checkout DESIRED_TAG
    * cd ..
    * git add Pillow
    * git commit

* Check minimum numpy versions to build against in ``.travis.yml`` file.  You
  need to build against the earliest numpy that Pillow is compatible with;
  see `forward, backward numpy compatibility
  <http://stackoverflow.com/questions/17709641/valueerror-numpy-dtype-has-the-wrong-size-try-recompiling/18369312#18369312>`_

The wheels get uploaded to a `rackspace container
<http://cdf58691c5cf45771290-6a3b6a0f5f6ab91aadc447b2a897dd9a.r50.cf2.rackcdn.com/>`_.  The credentials for this container
are encrypted to this specific repo in the ``.travis.yml`` file, so the upload
won't work for you from another repo.  
