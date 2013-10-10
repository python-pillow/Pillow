About Pillow
============

Goals
-----

The fork authors' goal is to foster active development of PIL through:

- Continuous integration testing via `Travis CI`_
- Publicized development activity on `GitHub`_
- Regular releases to the `Python Package Index`_
- Solicitation for community contributions and involvement on `Image-SIG`_

.. _Travis CI: https://travis-ci.org/python-imaging/Pillow
.. _GitHub: https://github.com/python-imaging/Pillow
.. _Python Package Index: https://pypi.python.org/pypi/Pillow
.. _Image-SIG: http://mail.python.org/mailman/listinfo/image-sig

Why a fork?
-----------

PIL is not setuptools compatible. Please see `this Image-SIG post`_ for a more
detailed explanation. Also, PIL's current bi-yearly (or greater) release
schedule is too infrequent to accomodate the large number and frequency of
issues reported.

.. _this Image-SIG post: https://mail.python.org/pipermail/image-sig/2010-August/006480.html

What about the official PIL?
----------------------------

.. note::

    Prior to Pillow 2.0.0, very few image code changes were made. Pillow 2.0.0
    added Python 3 support and includes many bug fixes from many contributors.

As more time passes since the last PIL release, the likelyhood of a new PIL
release decreases. However, we've yet to hear an official "PIL is dead"
announcement. So if you still want to support PIL, please
`report issues here first`_, then
`open the corresponding Pillow tickets here`_.

.. _report issues here first: https://bitbucket.org/effbot/pil-2009-raclette/issues

.. _open the corresponding Pillow tickets here: https://github.com/python-imaging/Pillow/issues

Please provide a link to the PIL ticket so we can track the issue(s) upstream.
