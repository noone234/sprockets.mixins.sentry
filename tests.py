"""
Tests for the sprockets.mixins.sentry package

"""
import os
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from tornado import testing, web
import raven
import tornado

from sprockets.mixins import sentry

VALUES = {'PGSQL_DSN': 'postgres://foo:bar@localhost:5432/dbname',
          'RABBITMQ_DSN': 'amqp://sentry:rabbitmq@localhost:5672/%2f',
          'VIRTUAL_ENV': '/Users/gavinr/Environments/sprockets'}
EXPECTATIONS = {'PGSQL_DSN': 'postgres://foo:****@localhost:5432/dbname',
                'RABBITMQ_DSN': 'amqp://sentry:****@localhost:5672/%2f',
                'VIRTUAL_ENV': '/Users/gavinr/Environments/sprockets'}

os.environ['SENTRY_DSN'] = (
    'https://00000000000000000000000000000000:'
    '00000000000000000000000000000000@app.getsentry.com/0')


class TestRequestHandler(sentry.SentryMixin, web.RequestHandler):
    send_to_sentry = mock.Mock()

    def initialize(self):
        super(TestRequestHandler, self).initialize()
        self.sentry_client.send = self.send_to_sentry
        self.send_to_sentry.reset_mock()

    def get(self, action):
        if action == 'fail':
            raise RuntimeError('something unexpected')
        if action == 'http-error':
            raise web.HTTPError(500)
        if action == 'web-finish':
            raise web.Finish()
        if action == 'add-tags':
            self.sentry_tags['some_tag'] = 'some_value'
            raise RuntimeError
        self.set_status(int(action))
        self.finish()


class TestDSNPasswordMask(unittest.TestCase):

    def test_password_masking(self):
        x = sentry.SentryMixin()
        x._strip_uri_passwords(VALUES)
        self.assertDictEqual(VALUES, EXPECTATIONS)


class ApplicationTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        self.sentry_client = TestRequestHandler.send_to_sentry
        app = web.Application([web.url(r'/(\S+)', TestRequestHandler)])
        return app

    def get_sentry_message(self):
        if TestRequestHandler.send_to_sentry.called:
            _, _, message = TestRequestHandler.send_to_sentry.mock_calls[0]
            return message
        return None

    def test_that_request_data_is_included(self):
        self.fetch('/fail')
        message = self.get_sentry_message()
        self.assertEqual(message['request']['url'], self.get_url('/fail'))
        self.assertEqual(message['request']['method'], 'GET')
        self.assertEqual(message['request']['data'], b'')

    def test_that_extra_data_is_included(self):
        self.fetch('/fail')
        message = self.get_sentry_message()
        extra = message['extra']
        self.assertEqual(
            extra['handler'],
            "'sprockets.mixins.sentry.{0}'".format(
                TestRequestHandler.__name__))

    def test_that_time_spent_is_nonzero(self):
        self.fetch('/fail')
        message = self.get_sentry_message()
        self.assertGreater(int(message['time_spent']), 0)

    def test_that_tags_are_sent(self):
        self.fetch('/add-tags')
        message = self.get_sentry_message()
        self.assertEqual(message['tags']['some_tag'], 'some_value')

    def test_that_modules_are_sent(self):
        self.fetch('/fail')
        message = self.get_sentry_message()
        self.assertEqual(message['modules']['raven'], raven.VERSION)
        self.assertEqual(message['modules']['sprockets.mixins.sentry'],
                         sentry.__version__)
        self.assertEqual(message['modules']['sys'], sys.version)
        self.assertEqual(message['modules']['tornado'], tornado.version)

    def test_that_status_codes_are_not_reported(self):
        self.fetch('/400')
        self.assertIsNone(self.get_sentry_message())

    def test_that_http_errors_are_not_reported(self):
        self.fetch('/http-error')
        self.assertIsNone(self.get_sentry_message())

    def test_that_web_finish_is_not_reported(self):
        self.fetch('/web-finish')
        self.assertIsNone(self.get_sentry_message())
