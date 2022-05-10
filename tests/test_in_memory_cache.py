import asynctest
from time import sleep

from plugins.cache.adapter import InMemoryStorage

cache = InMemoryStorage(cache={})


class TestInMemoryCache(asynctest.TestCase):

    async def test_get_and_delete(self):
        await cache.set("123", "123")

        value = await cache.get("123")

        self.assertEqual("123", value)

        await cache.delete("123")

        value = await cache.get("123")

        self.assertEqual(value, None)

    async def test_get_with_none(self):
        await cache.set("123", "123")

        data = await cache.get("1234")

        self.assertEqual(data, None)

        await cache.delete("123")

    async def test_get_with_timeout(self):
        await cache.set("123", "123", 3)

        self.assertEqual("123", await cache.get("123"))

        sleep(4)

        self.assertEqual(None, await cache.get("123"))
