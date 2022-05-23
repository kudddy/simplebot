import logging

from plugins.core.message_schema import Updater
from plugins.core.statemachine import Systems

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


async def hello(m: Updater,
                systems: Systems):
    chat_id = m.get_chat_id()

    # пишем чтобы активировать сессию
    text = "Привет❗"

    await systems.bot.send_message(chat_id,
                                   text)

    return 1


async def get_present(m: Updater,
                      systems: Systems):
    chat_id = m.get_chat_id()

    # пишем чтобы активировать сессию
    text = "Вот твой подарок❗"

    await systems.bot.send_message(chat_id,
                                   text)

    return 1


async def goodbye(m: Updater,
                  systems: Systems):
    chat_id = m.get_chat_id()

    # пишем чтобы активировать сессию
    text = "Пока❗"

    await systems.bot.send_message(chat_id,
                                   text)

    return 1


async def where_food(m: Updater,
                     systems: Systems):
    chat_id = m.get_chat_id()

    # пишем чтобы активировать сессию
    text = "В холодильнике❗"

    await systems.bot.send_message(chat_id,
                                   text)

    return 1


async def nothing_fount(m: Updater,
                        systems: Systems):
    chat_id = m.get_chat_id()
    # пишем чтобы активировать сессию
    text = "Простите, но не понял вас❗"

    await systems.bot.send_message(chat_id,
                                   text)

    return 1


async def lolo(m: Updater,
               systems: Systems):
    systems.model.predict()
