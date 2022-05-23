import logging

from aiohttp.web_app import Application
from aiomcache import Client

from ...core.config import setting
from ...core.helper import Coder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.setLevel(logging.INFO)


async def setup_mc(app: Application):
    log.info("Connecting to mc %r - %r",
             setting.app.hosts.mc.host,
             setting.app.hosts.mc.port)

    app['mc'] = Client(
        setting.app.hosts.mc.host,
        setting.app.hosts.mc.port,
    )

    await app['mc'].set(Coder.encode("123"), Coder.encode("345"))

    res = await app['mc'].get(Coder.encode("123"))

    assert Coder.decode(res) == "345"

    log.info("Success connect to %r - %r",
             setting.app.hosts.mc.host,
             setting.app.hosts.mc.port)
    try:
        yield
    finally:
        log.info('Disconnecting from mc')
        await app['mc'].close()
        log.info('Disconnected from mc')

