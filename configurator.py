from plugins.core.classifier import Model
from aiohttp.web_app import Application

from plugins.callback import hello_message, processor_photo, \
    goodbye_message, delete_from_ban, change_model, delete_data_from_table
from plugins.core.config import cfg
from plugins.tools.tokenizer import QueryBuilder
from plugins.mc.init import AioMemCache
from plugins.core.bot import Bot
from plugins.core.statemachine import Stages
from plugins.core.statemachine import Systems

train_data: dict = {
    "*": 1,
    "Выход": 2,
    "Подписался": 4,
    "/changemodel": 5,
    "удалитьданные": 6
}

model = Model()

model.fit(train_data)

# коллбэк функции
state = {
    0: hello_message,
    1: processor_photo,
    3: goodbye_message,
    4: delete_from_ban,
    5: change_model,
    6: delete_data_from_table
}


async def init_stages(app: Application):
    # инициализация объектов(возможно стоит сделать в качестве динамически
    # подключаемых плагинов)

    systems = Systems(mc=AioMemCache(app['mc']),
                      pg=app['pg'],
                      tokenizer=QueryBuilder(out_clean='str', out_token='list'),
                      bot=Bot(token=cfg.app.constants.bot_token),
                      mod=model,
                      permission=True,
                      user_model=cfg.app.constants.default_model)

    app['stage'] = Stages(state, systems)
