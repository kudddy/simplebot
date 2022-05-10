import logging
import asyncio

from types import AsyncGeneratorType, MappingProxyType
from typing import AsyncIterable, Mapping

import aiohttp_cors
from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp.web import run_app
from aiohttp_apispec import setup_aiohttp_apispec

from handlers import HANDLERS
from payloads import AsyncGenJSONListPayload, JsonPayload

from configurator import init_stages, stage

api_address = "0.0.0.0"
api_port = 8081

MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class Updater:

    @staticmethod
    def _create_app_hook() -> Application:
        """
        Создает экземпляр приложения, готового к запуску
        """
        app = Application(
            client_max_size=MAX_REQUEST_SIZE
        )
        aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        # # регистрируем коннектор к pg(синглтон)
        # app.cleanup_ctx.append(setup_pg)
        # # регистрируем коннектор к mc
        # app.cleanup_ctx.append(setup_mc)

        app.on_startup.append(init_stages)
        # Регистрация обработчика
        for handler in HANDLERS:
            log.debug('Registering handler %r as %r', handler, handler.URL_PATH)

            route = app.router.add_route('*', handler.URL_PATH, handler)

            app['aiohttp_cors'].add(route)

        setup_aiohttp_apispec(app=app, title="SIMPLE BOT", swagger_path='/')
        # Автоматическая сериализация в json данных в HTTP ответах
        PAYLOAD_REGISTRY.register(AsyncGenJSONListPayload,
                                  (AsyncGeneratorType, AsyncIterable))
        PAYLOAD_REGISTRY.register(JsonPayload, (Mapping, MappingProxyType))
        return app

    def run_hook(self):
        run_app(self._create_app_hook())

    @staticmethod
    async def _create_app_pulling():
        offset = 0
        while True:
            resp = await stage.systems.bot.get_updates(offset=offset)
            if resp != -1 and resp.ok and len(resp.result) > 0:
                try:
                    for res in resp.result:
                        await stage.next(res)

                except Exception as e:
                    log.info(f"troubles, error - {str(e)}")

                offset = resp.result[-1].update_id + 1

    # TODO сделать через очередь с ограничением кол-во обрабатываемых корутин
    def run_pulling(self):
        asyncio.run(self._create_app_pulling())
