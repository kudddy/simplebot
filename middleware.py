import functools
import asyncio

from plugins.core.message_schema import Updater
from plugins.core.statemachine import Systems
from plugins.pg.query import insert_date_to_audit, get_count_call_state_photo, \
    check_user_in_black_list, add_user_to_black_list, check_user_in_white_list, select_user_model

from plugins.core.config import cfg


def audit():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(m: Updater,
                          systems: Systems):
            state_name = func.__name__

            query = insert_date_to_audit(user_id=m.get_user_id(),
                                         chat_id=m.get_chat_id(),
                                         username=m.get_username(),
                                         state_name=state_name)

            await systems.pg.fetch(query)

            return await func(m, systems)

        return wrapped

    return wrapper


def check_user_permission():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(m: Updater,
                          systems: Systems):

            # toggle для отключения функционала
            if not cfg.app.constants.use_black_list:
                return await func(m, systems)

            async_tasks = [
                systems.pg.fetchval(check_user_in_white_list(m.get_user_id())),
                systems.pg.fetchval(check_user_in_black_list(m.get_user_id())),
                systems.pg.fetchval(get_count_call_state_photo(user_id=m.get_user_id()), column=1),
                systems.pg.fetchval(select_user_model(user_id=m.get_user_id()))
            ]

            permission_white, permission_black, count_req, user_model = await asyncio.gather(*async_tasks)

            if user_model:
                systems.user_model = user_model

            if permission_white:
                systems.permission = True
                return await func(m, systems)

            if permission_black:
                systems.permission = False
                return await func(m, systems)

            # если больше N попыток загрузить фото, то кидаем в блэк лист
            if count_req and count_req > cfg.app.constants.numbers_of_attemp:
                systems.permission = False

                add_to_ban_query = add_user_to_black_list(m.get_user_id())

                await systems.pg.fetch(add_to_ban_query)
            else:
                # если все проверки пройдены
                systems.permission = True
            return await func(m, systems)

        return wrapped

    return wrapper
