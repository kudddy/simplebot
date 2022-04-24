from dataclasses import dataclass
from aiohttp.web_app import Application

from plugins.callback import hello, get_present, goodbye, where_food, nothing_fount
from plugins.core.config import cfg
from plugins.tools.tokenizer import QueryBuilder
from plugins.mc.init import AioMemCache
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

    @dataclass
    class Systems:
        # высокоуровневый доступ к memcached,
        mc = AioMemCache(app['mc'])
        pg = app['pg']
        tokenizer = QueryBuilder(out_clean='str', out_token='list')
        bot = Bot(token=cfg.app.constants.bot_token)
        mod = model
        permission = True
        user_model = cfg.app.constants.default_model

    app['stage'] = Stages(stages=state,
                          systems=Systems())
