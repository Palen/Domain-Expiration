#! /usr/bin/python3.5
from configparser import ConfigParser
import asyncio

from collector.whois import DomainExpiration
from server.conn import get_db_conn

config = ConfigParser()
config.read('config.conf')

db = get_db_conn(config)


@asyncio.coroutine
def get_domains():
    """
    Coroutine - Get all domains from db `DomainExpiration`
    """
    for domain in db.domains.find():
        domain = DomainExpiration(**domain)
        yield from domain.run()

if __name__ == '__main__':

    # Get event loop
    loop = asyncio.get_event_loop()

    loop.run_until_complete(get_domains())

    loop.close()

