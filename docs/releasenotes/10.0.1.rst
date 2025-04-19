10.0.1
------

Security
========

:cve:`2023-4863`: Updated install script and updated wheels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This release provides an updated install script and updated wheels to
include libwebp 1.3.2, preventing a potential heap buffer overflow in
WebP.

Other changes
=============

Updated tests to pass with latest zlib version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The release of zlib 1.3 caused one of the tests in the Pillow test suite to fail.
