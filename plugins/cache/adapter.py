import logging

from abc import ABCMeta, abstractmethod
from time import time

from typing import Dict, Any

from aiomcache import Client

from ..core.helper import Coder
from ..core.config import setting

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.setLevel(logging.INFO)


class CacheAdapter(metaclass=ABCMeta):

    @abstractmethod
    def get(self, key: str):
        ...

    @abstractmethod
    def set(self, key: str, value: object, timeout: int = -1):
        ...

    @abstractmethod
    def delete(self, key: str):
        ...


class InMemoryStorage(CacheAdapter):
    def __init__(self, cache: Dict[str, Any]):
        self.cache: Dict[str, Any] = cache

    async def get(self, key: str):
        data = self.cache.get(key, None)
        if not data:
            return None
        value, cache_time, timeout = data

        if timeout == -1:
            return value

        if time() - cache_time > timeout:
            self.cache.pop(key, None)
            return None

        return value

    async def set(self, key: str, value: object, timeout: int = -1) -> None:
        self.cache.update({key: (value, time(), timeout)})

    async def delete(self, key: str) -> None:
        self.cache.pop(key, None)


class AioMemCache(CacheAdapter):
    def __init__(self, mc: Client):
        self.cache = mc

    async def get(self, key: object) -> dict or None:
        value = await self.cache.get(Coder.encode(key))
        if value:
            value = Coder.decode(value)
        return value

    async def set(self, key: object, value: object, timeout: int = 0):
        await self.cache.set(Coder.encode(key), Coder.encode(value), exptime=timeout)

    async def delete(self, key: object):
        await self.cache.delete(Coder.encode(key))


class CacheProvider(CacheAdapter):
    def __init__(self):

        cache = self._get_adapter()

        if isinstance(cache, dict):
            self._cache = InMemoryStorage(cache=cache)
        elif isinstance(cache, Client):
            self._cache = AioMemCache(mc=cache)

    @staticmethod
    def _get_adapter():
        if setting.app.cache.cache_type == "inmemory":
            return dict()
        elif setting.app.cache.cache_type == "memcached":
            return Client(
                host=setting.app.hosts.mc.host,
                port=setting.app.hosts.mc.port
            )
        else:
            raise Exception(f"This adapter not implement yet - {setting.app.cache.cache_type}")

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value: object, timeout: int = -1):
        return self._cache.set(key, value, timeout)

    def delete(self, key: str):
        return self._cache.delete(key)
