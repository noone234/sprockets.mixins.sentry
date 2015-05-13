sprockets.mixins.sentry
=======================
A RequestHandler mixin for sending exceptions to Sentry

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------
``sprockets.mixins.sentry`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets.mixins.sentry>`_
and can be installed via ``pip`` or ``easy_install``:

.. code:: bash

  pip install sprockets.mixins.sentry

Documentation
-------------
https://sprocketsmixinssentry.readthedocs.org

Requirements
------------
-  `sprockets <https://github.com/sprockets/sprockets>`_

Example
-------
This examples demonstrates how to use ``sprockets.mixins.sentry``.

.. code:: python

    from sprockets.mixins import sentry
    from tornado import web

    class RequestHandler(sentry.SentryMixin, web.RequestHandler):
        """Requires a ``SENTRY_DSN`` environment variable is set with the
        DSN value provided by sentry.

        The Mixin should catch unhandled exceptions and report them to Sentry.

        """
        def get(self, *args, **kwargs):
            raise ValueError("This should send an error to sentry")


Version History
---------------
Available at https://sprocketsmixinssentry.readthedocs.org/en/latest/history.html

.. |Version| image:: https://img.shields.io/pypi/v/sprockets.mixins.sentry.svg?
   :target: http://badge.fury.io/py/sprockets.mixins.sentry

.. |Status| image:: https://img.shields.io/travis/sprockets/sprockets.mixins.sentry.svg?
   :target: https://travis-ci.org/sprockets/sprockets.mixins.sentry

.. |Coverage| image:: https://img.shields.io/codecov/c/github/sprockets/sprockets.mixins.sentry.svg?
   :target: https://codecov.io/github/sprockets/sprockets.mixins.sentry?branch=master

.. |Downloads| image:: https://img.shields.io/pypi/dm/sprockets.mixins.sentry.svg?
   :target: https://pypi.python.org/pypi/sprockets.mixins.sentry

.. |License| image:: https://img.shields.io/pypi/l/sprockets.mixins.sentry.svg?
   :target: https://sprocketsmixinssentry.readthedocs.org