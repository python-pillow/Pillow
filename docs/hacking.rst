===================
 Hacking on Pillow
===================

Found a bug?  Want to submit a feature?  This page will help you get
started with doing development on Pillow.

First, get the source::

    $ git clone https://github.com/python-pillow/Pillow.git
    $ cd Pillow

Install pre-requisits::

    $ virtualenv env
    $ . env/bin/activate
    $ pip install nose

Build the ``develop`` target::

    $ python setup.py develop

Check that all the tests pass in your environment::

    $ nosetests -vx Tests/test_*.py

Assuming all the tests pass successfully you're all set!  Go ahead and hack
away.  When you're ready to submit your work back to the Pillow project,
just `fork and submit a pull request
<https://help.github.com/articles/using-pull-requests/>`_ as usual.  You
will probably be asked to submit a new test along with your pull request.
