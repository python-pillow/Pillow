##################################
Archives for pillow library builds
##################################

This directory contains archives for libraries that will be built as part of
the Pillow build.

In general, there is no need to put library archives here, because the
``multibuild`` scripts will download them from their respective URLs.

But, ``multibuild`` will look in this directory before downloading from the
URL, so if there is a library that often fails to download, or you think might
fail to download, then download it to this directory and add it to the git
repository.

See the ``fetch_unpack`` routine in ``multibuild/common_utils.sh`` for the
logic, and the build recipes in ``multibuild/library_builders.sh`` for the
filename to give to the downloaded archive.
