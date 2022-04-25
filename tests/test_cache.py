import asynctest
from aiomcache import Client
from plugins.core.cache import CacheProvider
from plugins.core.config import setting


class AioMemTest(asynctest.TestCase):
    async def test_get_and_set_from_cache(self):
        # memcached = Client(
        #     .app.hosts.mc.host,
        #     cfg.app.hosts.mc.port,
        #     pool_size=2)
        #
        # mc = AioMemCache(memcached)
        #
        # value: dict = {"1": 2}
        #
        # await mc.set(123, value)
        #
        # res = await mc.get(123)
        #

        cache = CacheProvider()

        value: dict = {"1": 2}

        await cache.set("123", value)

        res = await cache.get("123")

        self.assertEqual(value, res)




