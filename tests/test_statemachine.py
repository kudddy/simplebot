import asynctest
import logging

from time import sleep

from plugins.core.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import setting
from plugins.cache.adapter import CacheProvider
from plugins.db.adapter import DbProvider
from plugins.core.statemachine import Stages
from plugins.core.statemachine import Systems
from plugins.core.classifier import Model
from plugins.core.bot import Bot

from plugins.core.message_schema import Updater

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
    cache = CacheProvider()

    db = DbProvider().init_adapter()

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
                      pg=db,
                      bot=Bot(token=setting.app.configuration.bot_token),
                      mod=model)

    stage = Stages(state, systems)

    return stage, cache, db


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
