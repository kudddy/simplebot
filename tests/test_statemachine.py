import asynctest
import logging
# from asyncpgsa import PG
# from aiomcache import Client
from time import sleep

from plugins.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import setting
from plugins.tools.tokenizer import QueryBuilder
from plugins.core.cache import CacheProvider
from plugins.core.db import DbProvider
from plugins.core.statemachine import Stages
from plugins.core.statemachine import Systems
from plugins.core.classifier import Model
from plugins.core.bot import Bot

from message_schema import Updater

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


def generate_payload(text: str):
    return {
        "update_id": 243475549,
        "message": {
            "message_id": 9450,
            "from": {
                "id": 81432612,
                "is_bot": False,
                "first_name": "Kirill",
                "username": "kkkkk_kkk_kkkkk",
                "language_code": "ru"
            },
            "chat": {
                "id": 81432612,
                "first_name": "Kirill",
                "username": "kkkkk_kkk_kkkkk",
                "type": "private"
            },
            "date": 1589404439,
            "text": text
        }
    }


async def init_stages():
    # Инициализируем соединие с mc
    # memcached = Client(
    #     cfg.app.hosts.mc.host,
    #     cfg.app.hosts.mc.port,
    #     pool_size=2)
    #
    # global_cache = AioMemCache(memcached)
    #
    # global_cache.cache.flush_all()



    # Инициализируем соединение с базой данных
    # pg = PG()
    #
    # pg_pool_min_size = 10
    # pg_pool_max_size = 10
    #
    # await pg.init(
    #     str(cfg.app.hosts.pg.url),
    #     min_size=pg_pool_min_size,
    #     max_size=pg_pool_max_size
    # )

    memcached = CacheProvider()

    pg = DbProvider()



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

    systems = Systems(mc=memcached,
                      pg=pg,
                      tokenizer=QueryBuilder(out_clean='str', out_token='list'),
                      bot=Bot(token=setting.app.configuration.bot_token),
                      mod=model,
                      permission=True,
                      user_model=None)

    stage = Stages(state, systems)

    return stage, memcached, pg


class TestInternalSystem(asynctest.TestCase):

    async def test_node_with_timeout(self):
        stage, memcached, pg = await init_stages()

        states = ["Привет", "Подарок", "пока", "еда"]

        for text in states:
            data = generate_payload(text)

            message = Updater(**data)

            # засыпаем чтобы вернуться в первоначальный стейн
            if text == "Cледующая":
                sleep(setting.app.configuration.timeout_for_chat + 2)

            state_number = await stage.next(message)

            if text == "Привет":
                log.debug("checking a positive thread when the user follows all the recommendations")
                log.debug("phrase check - hello")
                self.assertEqual(state_number, 0)
            elif text == "Подарок":
                log.debug("phrase check - python")
                log.debug("we remain in the same state, but go through all the recommendations")
                self.assertEqual(state_number, 2)
            elif text == "пока":
                log.debug("phrase check - yes")
                log.debug("we remain in the same state, but go through all the recommendations, but timeout")
                self.assertEqual(state_number, 3)
            elif text == "еда":
                log.debug("phrase check - yes")
                log.debug("we remain in the same state, but go through all the recommendations, but timeout")
                self.assertEqual(state_number, 4)

        # memcached.close()
        # pg.pool.close()

