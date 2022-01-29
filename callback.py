import logging
from datetime import datetime
from json import dumps

from aiohttp_requests import requests as async_req
from sqlalchemy import select

from message_schema import Updater
from plugins.core.statemachine import Systems
from plugins.core.config import cfg
from plugins.pg.tables import user_file_id_status
from plugins.middleware import audit, check_user_permission
from plugins.pg.query import delete_user_from_black_list, \
    add_user_to_white_list, select_user_model, update_user_model, \
    insert_user_model, delete_data_from_user_id_status

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


async def permission_message(m: Updater,
                             system: Systems):
    buttons = [
        [
            {

                "text": "Подписаться🤓❤",

                "url": "https://youtu.be/k28SlalrkgU",

            }
        ],
        [
            {

                "text": "Готово❤️",

                "callback_data": "Подписался",

            }
        ]

    ]
    text = "Вы запросили > {} фотографий. Для продолжения нажмите на кнопку Подписаться и подпишитесь, " \
           "пожалуйста,  на канал. " \
           "После нажатия на кнопку готово разблокируется возможность пользоваться ботом Спасибо❤ Вы очень " \
           "поможете развитию проекта❗".format(cfg.app.constants.numbers_of_attemp)
    await system.bot.send_message(m.get_chat_id(),
                                  text,
                                  inline_keyboard=buttons,
                                  remove_keyboard=True)


async def prepare_photo(m: Updater,
                        systems: Systems):
    chat_id = m.get_chat_id()
    user_id = m.get_user_id()
    username = m.get_username()
    file_id = m.get_file_id()
    status = "PENDING"

    log.debug("зашли в условие где мы обнаружили фото")
    text = '💥 Окей, я начинаю готовить для тебя фото.'

    buttons = [
        [
            {

                "text": "Понравилось? Подпишитесь на канал🤓❤",

                "callback_data": "",

                "url": "https://youtu.be/k28SlalrkgU",

            }
        ],
        [
            {

                "text": "Хочешь научиться так делать?❤️",

                "callback_data": "",

                "url": "https://youtu.be/k28SlalrkgU",

            }
        ],
        [
            {
                "text": "Проблемы с ботом? Пиши❤️️",

                "callback_data": "",

                "url": "https://t.me/kkkkk_kkk_kkkkk",
            }
        ]
    ]

    query = user_file_id_status.insert().values(
        user_id=user_id,
        chat_id=chat_id,
        username=username,
        date=datetime.now(),
        file_id=file_id,
        status=status
    )

    await systems.pg.fetch(query)

    log.debug("Отправили запрос в базу")

    if systems.user_model == "version 1":
        user_model = "version 1 (🔺 stylization, 🔻 robustness)"
    else:
        user_model = "version 2 (🔺 robustness,🔻 stylization)"

    payload = {
        "file_id": file_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "user_model": user_model
    }
    await async_req.post(cfg.app.hosts.sheduler.url,
                         data=dumps(payload),
                         ssl=False,
                         headers={'Content-Type': 'application/json'})

    await systems.bot.send_message(m.get_chat_id(),
                                   text,
                                   inline_keyboard=buttons,
                                   remove_keyboard=True)


@check_user_permission()
@audit()
async def hello_message(m: Updater,
                        systems: Systems):
    """
    Приветственное сообщение с просьбой указать навык
    :param systems: Объект с вспомогательными классами(для доступа к базам и локальному кэшу)
    :param m: Входящее сообщение
    :return: ключ колбэк ф-ции, которую нужно вызвать
    """

    if not systems.permission:
        await permission_message(m=m, system=systems)

        return 1

    chat_id = m.get_chat_id()
    file_id = m.get_file_id()

    await systems.mc.delete(chat_id)

    if file_id:
        await prepare_photo(m=m, systems=systems)
    else:
        # пишем чтобы активировать сессию
        text = "💥 Приветствую, я сгенерирую для тебя аниме фотографию. Старайтесь держать в кадре только лицо, " \
               "идеальный вариант представлен в примере. 🆘 Пожалуйста! Перед загрузкой, обрежьте " \
               "фотографию так, чтобы на ней было только лицо, иначе качество сильно пострадает! 🆘 Приятного " \
               "использования! Загрузите фото❗"

        await systems.bot.send_video(chat_id=chat_id,
                                     file_id="BAACAgIAAxkBAAMGYZ-a0gKp7u-MiET3e47927QHXsoAAlMWAAK-vwFJth7Zpb6XmrUiBA")

        await systems.bot.send_message(chat_id,
                                       text)

        return 1


@check_user_permission()
@audit()
async def processor_photo(m: Updater,
                          systems: Systems):
    if not systems.permission:
        await permission_message(m=m, system=systems)

        return 1

    user_id = m.get_user_id()
    file_id = m.get_file_id()

    query = select([user_file_id_status.c.status]).where(user_file_id_status.c.user_id == user_id)

    arr = [data['status'] for data in await systems.pg.fetch(query)]

    if len(arr) > 0:
        # пользователь уже был
        # если в базе есть инфы по юзеру, то блокируем процесс запуска воркера
        text = "Процесс уже запущен. Подождите пока завершится расчет предыдущего фото❗"
        await systems.bot.send_message(m.get_chat_id(),
                                       text,
                                       remove_keyboard=True)
    else:
        if file_id:
            await prepare_photo(m=m, systems=systems)
        else:
            text = 'Это не фото. Загрузи фото❗'
            await systems.bot.send_message(m.get_chat_id(),
                                           text,
                                           remove_keyboard=True)
    return 1


async def goodbye_message(m: Updater,
                          systems: Systems):
    text = '💥 Пока, возвращайся еще❗️'
    await systems.bot.send_message(m.get_chat_id(),
                                   text,
                                   remove_keyboard=True)
    return 0


@audit()
async def delete_from_ban(m: Updater,
                          systems: Systems):
    add_user_to_white_query = add_user_to_white_list(m.get_user_id())

    await systems.pg.fetch(add_user_to_white_query)

    delete_from_ban_query = delete_user_from_black_list(m.get_user_id())

    await systems.pg.fetch(delete_from_ban_query)

    text = 'Спасибо, что подписались на канал❗ Теперь вы имеете доступ без ограничений🤓 Загрузите фото❗'
    await systems.bot.send_message(m.get_chat_id(),
                                   text,
                                   remove_keyboard=True)

    return 1


@audit()
async def change_model(m: Updater,
                       systems: Systems):
    # отправляем запрос, если значение есть то меняем на друго
    user_id = m.get_user_id()

    query = select_user_model(user_id)

    data = await systems.pg.fetchval(query)

    if data:
        if data == "version 2":
            new_version = "version 1"

        else:
            new_version = "version 2"

        query = update_user_model(user_id=user_id,
                                  model_version=new_version)
    else:
        new_version = "version 1"
        query = insert_user_model(user_id=user_id,
                                  model_version=new_version)

    await systems.pg.fetch(query)

    text = "Стиль обработки изменен❗ Загрузить фото🤩"

    await systems.bot.send_message(m.get_chat_id(),
                                   text,
                                   remove_keyboard=True)

    return 1


async def delete_data_from_table(m: Updater,
                                 systems: Systems):
    query = delete_data_from_user_id_status()

    await systems.pg.fetch(query)

    text = "Удалено!"

    await systems.bot.send_message(m.get_chat_id(),
                                   text,
                                   remove_keyboard=True)

    return 1
