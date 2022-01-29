import logging

from types import AsyncGeneratorType, MappingProxyType
from typing import AsyncIterable, Mapping

from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec
import aiohttp_cors

from handlers import HANDLERS
from payloads import AsyncGenJSONListPayload, JsonPayload

from plugins.pg.connector import setup_pg
from plugins.mc.init import setup_mc
from plugins.configurator import init_stages

api_address = "0.0.0.0"
api_port = 8081

MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


def create_app() -> Application:
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
    # регистрируем коннектор к pg(синглтон)
    app.cleanup_ctx.append(setup_pg)
    # регистрируем коннектор к mc
    app.cleanup_ctx.append(setup_mc)

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
