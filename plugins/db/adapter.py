from asyncpgsa import PG
from abc import ABCMeta, abstractmethod
from typing import Union

from plugins.core.config import setting

CENSORED = '***'
DEFAULT_PG_URL = setting.app.db.config.url
MAX_QUERY_ARGS = 32767
MAX_INTEGER = 2147483647

pg_pool_min_size = 10
pg_pool_max_size = 10


class DbAdapter(metaclass=ABCMeta):

    @abstractmethod
    async def fetch(self, query):
        ...

    @abstractmethod
    async def fetchval(self, query):
        ...


class DbProvider(DbAdapter):
    def __init__(self):

        self.db = None

    async def init_adapter(self):
        self.db = await self._get_adapter()

    @staticmethod
    async def _get_adapter() -> Union[PG, None]:
        print(setting.app.db.db_type)
        if setting.app.db.db_type == "pg":
            return await PG().init(
                str(DEFAULT_PG_URL),
                min_size=pg_pool_min_size,
                max_size=pg_pool_max_size
            )
        elif setting.app.db.db_type == "inmemory":
            return None
        else:
            raise Exception(f"adapter not implement yet")

    async def fetch(self, query):
        return await self.db.fetch(query)

    async def fetchval(self, query):
        return await self.db.fetchval(query)
