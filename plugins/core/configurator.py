from dataclasses import dataclass
from aiohttp.web_app import Application

from plugins.core.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import setting
from plugins.cache.adapter import CacheProvider
from plugins.db.adapter import DbProvider
from plugins.core.bot import Bot
from plugins.core.statemachine import Stages
from plugins.core.classifier import Model

INIT_INTENT = 0

train_data: dict = {
    "*": 1,
    "Подарок": 2,
    "пока": 3,
    "еда": 4
}

model = Model()

model.fit(train_data)

# коллбэк функции
state = {
    INIT_INTENT: hello,
    1: nothing_fount,
    2: get_present,
    3: goodbye,
    4: where_food
}


### TODO вот это все должно быть под капотом

@dataclass
class Systems:
    # TODO need rename this adapter
    mc = CacheProvider()
    # TODO need to solve the problem with closing connection
    pg = DbProvider().init_adapter()

    bot = Bot(token=setting.app.configuration.bot_token)

    model = model


stage = Stages(stages=state,
               systems=Systems())


async def init_stages(app: Application):
    # инициализация объектов(возможно стоит сделать в качестве динамически
    # подключаемых плагинов)

    # TODO переименовать QueryBuilder

    # cache = CacheProvider()
    #
    # db = DbProvider()

    app['stage'] = stage
