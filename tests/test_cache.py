import asynctest
from plugins.cache.adapter import CacheProvider


# TODO tests are written only for local cache
class AioMemTest(asynctest.TestCase):
    async def test_get_and_set_from_cache(self):

        cache = CacheProvider()

        value: dict = {"1": 2}

        await cache.set("123", value)

        res = await cache.get("123")

        self.assertEqual(value, res)
