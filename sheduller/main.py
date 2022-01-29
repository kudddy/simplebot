import asyncio
from asyncpgsa import PG

from plugins.core.config import cfg
from plugins.pg.query import give_me_file_id_in_queen
from plugins.core.helper import get_file_path, get_file

loop = asyncio.get_event_loop()


async def generate_data():
    # Инициализируем соединение с базой данных
    pg = PG()

    pg_pool_min_size = 10
    pg_pool_max_size = 10

    await pg.init(
        str(cfg.app.hosts.pg.url),
        min_size=pg_pool_min_size,
        max_size=pg_pool_max_size
    )

    while True:
        query = give_me_file_id_in_queen()
        file_ids = []
        for row in await pg.fetch(query):
            file_ids.append(row['file_id'])

        file_paths = []
        for file_id in file_ids:
            path_file = get_file_path(file_id)
            file = get_file(path_file)
            print("получаем файл")


loop.run_until_complete(generate_data())
