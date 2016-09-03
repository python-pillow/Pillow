Depends
=======

``install_openjpeg.sh``, ``install_webp.sh`` and ``install_imagequant.sh`` can
be used to download, build & install non-packaged dependencies; useful for
testing with Travis CI.

The other scripts can be used to install all of the dependencies for
the listed operating systems/distros. The ``ubuntu_14.04.sh`` and
``debian_8.2.sh`` scripts have been tested on bare AWS images and will
install all required dependencies for the system Python 2.7 and 3.4
for all of the optional dependencies.  Git may also be required prior
to running the script to actually download Pillow.

e.g.::

  $ sudo apt-get install git
  $ git clone https://github.com/python-pillow/Pillow.git
  $ cd Pillow/depends
  $ ./debian_8.2.sh
  $ cd ..
  $ git checkout [branch or tag]
  $ virtualenv -p /usr/bin/python2.7 ~/vpy27
  $ source ~/vpy27/bin/activate
  $ make install
  $ make test

