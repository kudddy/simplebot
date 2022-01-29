from aiomcache import Client
import logging
from functools import wraps

from aiohttp.web_app import Application

from plugins.core.config import cfg
from plugins.core.helper import Coder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.setLevel(logging.INFO)


def encode_input_value(func):
    # TODO есть впечатление что операция блокирующая
    @wraps(func)
    async def wrapper(*args):
        result = await func(*tuple(Coder.encode(x) if not isinstance(x, AioMemCache) else x for x in args))
        if result:
            return Coder.decode(result)

    return wrapper


class AioMemCache:
    def __init__(self, mc: Client):
        self.cache = mc

    # @encode_input_value
    async def get(self, key: object) -> dict or None:
        value = await self.cache.get(Coder.encode(key))
        if value:
            value = Coder.decode(value)
        return value

    # @encode_input_value
    async def set(self, key: object, value: object, timeout: int = 0):
        await self.cache.set(Coder.encode(key), Coder.encode(value), exptime=timeout)

    # @encode_input_value
    async def delete(self, key: object):
        await self.cache.delete(Coder.encode(key))


async def setup_mc(app: Application):
    log.info("Connecting to mc %r - %r",
             cfg.app.hosts.mc.host,
             cfg.app.hosts.mc.port)

    app['mc'] = Client(
        cfg.app.hosts.mc.host,
        cfg.app.hosts.mc.port,
    )

    await app['mc'].set(Coder.encode("123"), Coder.encode("345"))

    res = await app['mc'].get(Coder.encode("123"))

    assert Coder.decode(res) == "345"

    log.info("Success connect to %r - %r",
             cfg.app.hosts.mc.host,
             cfg.app.hosts.mc.port)
    try:
        yield
    finally:
        log.info('Disconnecting from mc')
        await app['mc'].close()
        log.info('Disconnected from mc')

