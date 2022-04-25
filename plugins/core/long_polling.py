import logging
from asyncpgsa import PG

from plugins.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import setting
from plugins.tools.tokenizer import QueryBuilder
from plugins.core.cache import CacheProvider
from plugins.core.statemachine import Stages
from plugins.core.statemachine import Systems
from plugins.core.classifier import Model
from plugins.core.bot import Bot

from message_schema import Updater

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


async def init_stages():
    # # Инициализируем соединие с mc
    # memcached = Client(
    #     cfg.app.hosts.mc.host,
    #     cfg.app.hosts.mc.port,
    #     pool_size=2)
    #
    # global_cache = AioMemCache(memcached)
    #
    # global_cache.cache.flush_all()

    memcached = None

    memory = {}

    cache = CacheProvider(cache=memory)

    # Инициализируем соединение с базой данных
    pg = PG()

    pg_pool_min_size = 10
    pg_pool_max_size = 10

    await pg.init(
        str(setting.app.hosts.pg.url),
        min_size=pg_pool_min_size,
        max_size=pg_pool_max_size
    )



    train_data: dict = {
        "*": 1,
        "Выход": 2,
        "Подарок": 2,
        "пока": 3,
        "еда": 4
    }

    model = Model()

    model.fit(train_data)

    # коллбэк функции
    state = {
        0: hello,
        1: nothing_fount,
        2: get_present,
        3: goodbye,
        4: where_food
    }

    systems = Systems(mc=cache,
                      pg=pg,
                      tokenizer=QueryBuilder(out_clean='str', out_token='list'),
                      bot=Bot(token=setting.app.constants.bot_token),
                      mod=model,
                      permission=True,
                      user_model=setting.app.constants.default_model)

    stage = Stages(state, systems)

    return stage, memcached, pg


async def run_loop():
    stage, memcached, pg = await init_stages()

    stage.systems.bot.get_updates()
    offset = 0
    while True:
        resp = stage.systems.bot.get_updates(offset=offset)
        if resp != -1 and resp.ok and len(resp.result) > 0:
            #
            for updates in resp.result:
                try:

                    message = Updater(**updates)

                    await stage.next(message)



                except Exception as e:
                    log.info(f"troubles, error - {str(e)}")

                offset = updates.update_id + 1
