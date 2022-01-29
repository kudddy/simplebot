import asynctest
from aiomcache import Client
from plugins.mc.init import AioMemCache
from plugins.core.config import cfg


class AioMemTest(asynctest.TestCase):
    async def test_get_and_set_from_cache(self):
        memcached = Client(
            cfg.app.hosts.mc.host,
            cfg.app.hosts.mc.port,
            pool_size=2)

        mc = AioMemCache(memcached)

        value: dict = {"1": 2}

        await mc.set(123, value)

        res = await mc.get(123)

        self.assertEqual(value, res)
