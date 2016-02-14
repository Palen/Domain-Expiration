import unittest
import asyncio
import asynctest
from random import choice
from collections import namedtuple

from .valid_whois_resp import valid_resp
from collector.whois import DomainExpiration


class WhoisMeMock:

    @asyncio.coroutine
    def mock_whois_me(self, resp=valid_resp):
        yield from asyncio.sleep(0.1)
        return resp


@asyncio.coroutine
def mock_process(resp):
    yield from asyncio.sleep(0.1)
    return resp


@asyncio.coroutine
def mock_comunicate(resp=valid_resp):
    yield from asyncio.sleep(0.1)
    return resp, None


class TestWhoisDomainExpiration(unittest.TestCase):

    def setUp(self):
        self.P = namedtuple('FakeProcess', ['communicate', 'returncode'])
        self.fields = ['name', 'register', 'creation_date', 'expiration_date', 'updated_date', 'last_info_date']

    def test_domain_expiration_instance_ok(self):
        valid_domain = 'albertpalenzuela.com'
        domain_expiration = DomainExpiration(domain=valid_domain)
        self.assertTrue(domain_expiration.allowed)
        self.assertEqual(domain_expiration.name, 'albertpalenzuela.com')
        self.assertEqual(domain_expiration.dom, 'com')
        for field in self.fields:
            self.assertTrue(hasattr(domain_expiration, field))

    def test_domain_expiration_instance_ko(self):
        invalid_domain = choice([None, 0, dict(), []])
        with self.assertRaises(ValueError) as exc:
            DomainExpiration(domain=invalid_domain)
            self.assertEqual(exc, 'Invalid {0}/{1}.'.format(invalid_domain, type(invalid_domain)))

    def test_domain_with_www_ok(self):
        valid_domain = 'www.albertpalenzuela.com'
        domain_expiration = DomainExpiration(domain=valid_domain)
        self.assertEqual(domain_expiration.name, 'albertpalenzuela.com')

    def test_invalid_domain_ok(self):
        invalid_domain = 'albertpalenzuela.es'
        domain_expiration = DomainExpiration(domain=invalid_domain)
        self.assertFalse(domain_expiration.allowed)

    def test_get_dom(self):
        valid_domain = 'albertpalenzuela.co.jp'
        domain_expiration = DomainExpiration(domain=valid_domain)
        self.assertEqual(domain_expiration.dom, 'co_jp')

    def test_domain_to_dict(self):
        # Without name
        domain_expiration = DomainExpiration(domain='albertpalenzuela.com')
        self.assertTrue('name' not in domain_expiration.to_dict())
        # With name
        self.assertTrue('name' in domain_expiration.to_dict(name=True))

    def test_whois_me(self):
        domain_expiration = DomainExpiration(domain='albertpalenzuela.com')
        with asynctest.mock.patch('asyncio.subprocess.create_subprocess_exec') as sub_proc:
            sub_proc.return_value = self.P(mock_comunicate, 0)
            resp = asyncio.get_event_loop().run_until_complete(
               domain_expiration.whois_me())
            self.assertEqual(resp, valid_resp.decode())
            self.assertEqual(domain_expiration.available, False)
            # Return code 1
            sub_proc.return_value = self.P(mock_comunicate, 1)
            resp = asyncio.get_event_loop().run_until_complete(
               domain_expiration.whois_me())
            self.assertEqual(resp, valid_resp.decode())
            self.assertEqual(domain_expiration.available, True)
            # Different return code
            from functools import partial
            sub_proc.return_value = self.P(partial(mock_comunicate, ''), choice(range(2, 10)))
            with self.assertRaises(Exception) as e:
                asyncio.get_event_loop().run_until_complete(
                domain_expiration.whois_me())
                self.assertEqual('', e)

