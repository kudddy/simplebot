from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
# aiohttp_cors.WebViewMixig

from aiohttp_cors import CorsViewMixin


class BaseView(View, CorsViewMixin):
    URL_PATH: str

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @property
    def stage(self):
        return self.request.app['stage']
