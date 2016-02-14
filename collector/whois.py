import re
import sys
import asyncio
import datetime
from copy import copy

from collector import regex_map
from main import config
from server.conn import get_db_conn


class DomainExpiration:
    """
    Main representation of a Domain
    """

    fields = ['name', 'register', 'creation_date', 'expiration_date', 'updated_date', 'last_info_date']

    def __init__(self, domain=None, **attrs):
        domain = domain or attrs.get('name', None)
        if not isinstance(domain, str):
            raise ValueError('Invalid {0}/{1}.'.format(domain, type(domain)))
        domain = domain.lower()
        if 'www.' in domain:
            domain = domain.split('www.')[-1]
        self.name = domain
        self.dom = self._get_dom_()

        # Is it a valid domain?
        try:
            getattr(regex_map, self.dom)
            self.allowed = True
        except AttributeError:
            self.allowed = False

        # Initialize not available
        self.available = False

        # Mongo Cursor
        self.db = get_db_conn(config)

        # Initialize Domain attrs
        for field in self.fields[1:]:
            setattr(self, field, attrs.get(field, None))

    def _get_dom_(self):
        """
        Get the ending part of the url ex: google.[com]
        :return: {String}
        """
        if self.name.endswith('.co.jp'):
            return 'co_jp'
        else:
            return self.name.split('.')[-1]

    def to_dict(self, name=False):
        """
        Serialize the instance into a {Dict}
        :param name: {Bool} serialize with name?
        :return: {Dict}
        """
        fields = self.fields if name else self.fields[1:]
        ret = dict()
        for field in fields:
            ret.update({field: getattr(self, field, None)})
        return ret

    async def whois_me(self):
        """
        whois wrapper - Based on the whois linux command.
        resp = loop.run_until_complete(self.whois_me())
        :return {String} - resp
        """
        process = await asyncio.subprocess.create_subprocess_exec(*['/usr/bin/whois', self.name],
                                                                  stdout=asyncio.subprocess.PIPE,
                                                                  stderr=asyncio.subprocess.STDOUT)
        resp, _ = await process.communicate()
        try:
            resp = resp.decode('utf-8')
        except UnicodeDecodeError:
            resp = resp.decode('latin-1')

        if process.returncode == 1:
            self.available = True
        elif process.returncode != 0:
            raise Exception(resp)

        return resp

    def parse_whois(self, data_str):
        """
        Get the whois info and assign it into cls.fields attributes
        :param data_str: {String} - Whois info
        """
        self.last_info_date = str(datetime.datetime.now())
        for field in self.fields[1:-1]:
            if self.available:
                setattr(self, field, 'AVAILABLE')
                continue
            try:
                regex_dom = copy(getattr(regex_map, self.dom))
                while regex_dom.get('extend'):
                    extend = regex_dom.pop('extend')
                    regex_dom.update(copy(getattr(regex_map, extend)))
                matches = re.search(regex_dom[field], data_str)
                if matches.groups():
                    setattr(self, field, matches.groups()[0])
            except AttributeError:
                sys.stderr.write("Domain not available: %s" % self.dom)
                break
            except KeyError:
                setattr(self, field, "ERROR")
                sys.stderr.write("Field: %s not matched in domain: %s" % (field, self.name))
            except Exception as e:
                setattr(self, field, "ERROR")
                sys.stderr.write("Unexpected Exception: %s" % e)

    def save(self):
        """
        Store or update into db.
        :return: Domain instance
        """
        domain = self.db.domains.update_one({'name': self.name}, {"$set": self.to_dict()}, True)
        return domain

    @asyncio.coroutine
    def run(self):
        """
        Update the whois info from protocol to database.
        :return: Domain instance
        """
        data_str = yield from self.whois_me()
        self.parse_whois(data_str)
        domain = self.save()
        return domain

