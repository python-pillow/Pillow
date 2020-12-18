About
=====

Goals
-----

The fork author's goal is to foster and support active development of PIL through:

- Continuous integration testing via `GitHub Actions`_, `AppVeyor`_ and `Travis CI`_
- Publicized development activity on `GitHub`_
- Regular releases to the `Python Package Index`_

.. _GitHub Actions: https://github.com/python-pillow/Pillow/actions
.. _AppVeyor: https://ci.appveyor.com/project/Python-pillow/pillow
.. _Travis CI: https://travis-ci.com/github/python-pillow/pillow-wheels
.. _GitHub: https://github.com/python-pillow/Pillow
.. _Python Package Index: https://pypi.org/project/Pillow/

License
-------

Like PIL, Pillow is `licensed under the open source HPND License <https://raw.githubusercontent.com/python-pillow/Pillow/master/LICENSE>`_

Why a fork?
-----------

PIL is not setuptools compatible. Please see `this Image-SIG post`_ for a more detailed explanation. Also, PIL's current bi-yearly (or greater) release schedule is too infrequent to accommodate the large number and frequency of issues reported.

.. _this Image-SIG post: https://mail.python.org/pipermail/image-sig/2010-August/006480.html

What about PIL?
---------------

.. note::

    Prior to Pillow 2.0.0, very few image code changes were made. Pillow 2.0.0
    added Python 3 support and includes many bug fixes from many contributors.

As more time passes since the last PIL release (1.1.7 in 2009), the likelihood of a new PIL release decreases. However, we've yet to hear an official "PIL is dead" announcement.
