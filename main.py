#! /usr/bin/python3.5
from configparser import ConfigParser

from aiohttp import web
import aiohttp_jinja2
import jinja2


config = ConfigParser()
config.read('config.conf')


if __name__ == '__main__':
    from server.views import IndexView, AddDomainView, UpdateDomainView
    app = web.Application()
    # Routes
    app.router.add_route('*', '/', IndexView)
    app.router.add_route('*', '/add/', AddDomainView, expect_handler=web.Request.json)
    app.router.add_route('*', '/update/', UpdateDomainView)
    # Static
    if bool(config.get('MAIN', 'DEBUG')):
        app.router.add_static('/static/', 'static/')

    # Add templates
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))

    web.run_app(app)