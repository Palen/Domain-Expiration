
from aiohttp import web
import aiohttp_jinja2

from server.conn import get_db_conn
from main import config
from collector.whois import DomainExpiration


class CustomView(web.View):
    """
    aiohttp.web.View with db attribute
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = get_db_conn(config)


class IndexView(CustomView):
    """
    Handle for view /
    """
    def _get_domains_(self):
        for domain in self.db.domains.find().sort("name"):
            yield DomainExpiration(**domain)

    async def get(self):
        return await self._get_(self.request)

    @aiohttp_jinja2.template('index.html')
    def _get_(self, request):
        return {'domains': list(self._get_domains_())}


class AddDomainView(CustomView):
    """
    Handle for view /add/
    """
    EMPTY_DOMAIN = "Domain field is mandatory."
    EXISTS = "Domain already exists"
    ALLOWED = "Domain not allowed."

    async def post(self):
        return await self._post_(self.request)

    async def _post_(self, request):
        data = await request.post()
        domain = data.get('domain', "")
        domain_expiration = DomainExpiration(domain=domain)

        if not domain_expiration.name:
            response = {"response": "KO", "message": self.EMPTY_DOMAIN}
        elif not domain_expiration.allowed:
            response = {"response": "KO", "message": self.ALLOWED}

        elif self.db.domains.find_one({"name": domain_expiration.name}):
            response = {"response": "KO", "message": self.EXISTS}

        else:
            domain_expiration.save()
            response = {"response": "OK"}

        return web.json_response(response)


class UpdateDomainView(CustomView):
    """
    Handle for view /update/
    """

    async def post(self):
        return await self._post_(self.request)

    async def _post_(self, request):
        data = await request.post()
        domain = self.db.domains.find_one({"name": data.get('name')})
        if not domain:
            response = {"response": "KO", "message": "HTML 5 fff"}
        else:
            try:
                domain_expiraton = DomainExpiration(**domain)
                await domain_expiraton.run()
                response = {"response": "OK"}
            except Exception as e:

                response = {"response": "KO", "message": str(e)}
        return web.json_response(response)


# class LoginView(CustomView):
#     """
#     Handle for view /login/
#     """
#
#     async def get(self):
#         return await self._get_(self.request)
#
#     @aiohttp_jinja2.template('login.html')
#     def _get_(self, request):
#         pass
#
#     async def post(self):
#         return await self._post_(self.request)
#
#     def _post_(self, request):
#         pass
