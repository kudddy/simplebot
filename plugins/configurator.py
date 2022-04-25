from dataclasses import dataclass
from aiohttp.web_app import Application

from plugins.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import setting
from plugins.tools.tokenizer import QueryBuilder
from plugins.core.cache import CacheProvider
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


async def init_stages(app: Application):
    # инициализация объектов(возможно стоит сделать в качестве динамически
    # подключаемых плагинов)

    # TODO переименовать QueryBuilder

    # TODO add flag in settings to select cache adapter

    @dataclass
    class Systems:
        # высокоуровневый доступ к memcached,
        # mc = AioMemCache(app['mc'])
        mc = CacheProvider()
        pg = app['pg']
        tokenizer = QueryBuilder(out_clean='str', out_token='list')
        bot = Bot(token=setting.app.constants.bot_token)
        mod = model
        permission = True
        user_model = setting.app.constants.default_model

    app['stage'] = Stages(stages=state,
                          systems=Systems())
