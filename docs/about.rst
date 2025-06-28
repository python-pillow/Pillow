About
=====

Goals
-----

The fork author's goal is to foster and support active development of PIL through:

- Continuous integration testing via `GitHub Actions`_
- Publicized development activity on `GitHub`_
- Regular releases to the `Python Package Index`_

.. _GitHub Actions: https://github.com/python-pillow/Pillow/actions
.. _GitHub: https://github.com/python-pillow/Pillow
.. _Python Package Index: https://pypi.org/project/pillow/

License
-------

Like PIL, Pillow is `licensed under the open source MIT-CMU License <https://raw.githubusercontent.com/python-pillow/Pillow/main/LICENSE>`_

Why a fork?
-----------

PIL is not setuptools compatible. Please see `this Image-SIG post`_ for a more detailed explanation. Also, PIL's bi-yearly (or greater) release schedule was too infrequent to accommodate the large number and frequency of issues reported.

.. _this Image-SIG post: https://mail.python.org/pipermail/image-sig/2010-August/006480.html

What about PIL?
---------------

.. note::

    Prior to Pillow 2.0.0, very few image code changes were made. Pillow 2.0.0
    added Python 3 support and includes many bug fixes from many contributors.

The last PIL release was in 2009 (1.1.7) and `no future releases are expected <https://github.com/python-pillow/Pillow/issues/1535>`_. In January 2020, `the PyPI moderators exhausted the PEP 541 process for contacting the PIL project owner <https://github.com/python-pillow/Pillow/issues/1535#issuecomment-570308446>`_ and the `PIL project on PyPI <https://pypi.org/project/PIL>`_ was transferred to the `Pillow team <https://github.com/python-pillow/Pillow/graphs/contributors>`_. The Pillow team has no plans to update the PIL project on PyPI.
