from message_schema import Updater

from plugins.core.config import cfg


# TODO паразитная зависимость

class Systems:
    def __init__(self,
                 mc,
                 pg,
                 tokenizer,
                 bot,
                 mod,
                 permission,
                 user_model):
        self.mc = mc
        self.pg = pg
        self.tokenizer = tokenizer
        self.bot = bot
        self.model = mod
        self.permission = permission
        self.user_model = user_model


class Stages:
    def __init__(self,
                 stages: dict,
                 systems: Systems):
        self.stages = stages
        self.systems = systems

    @property
    def k_iter(self):
        return len(self.stages) - 1

    async def next(self,
                   m: Updater) -> int:
        """
        Ф-ция занимается маршрутизацией и вызовом коллбэк функций
        :param m: сообщение от Telegram
        :return: None
        """
        text = m.get_text()
        chat_id = m.get_chat_id()
        # запрашиваем глобальный кэш
        key = await self.systems.mc.get(chat_id)
        # если есть то смотрим на шаг
        if key:
            # если сессия активирована,то запускаем классификатор
            step = self.systems.model.predict(text=text)
        # если нет, то в начальном стейте
        else:
            step = 0

        # вызываем функцию соответствующу стейту
        await self.stages[step].__call__(m, self.systems)

        # достаем сессионные данные
        key = await self.systems.mc.get(chat_id)

        # если пользователь уже в стейте, то перезаписываем стейт
        if key:
            key['step'] = step
        else:
            # если нет, то создаем новый
            key = {'step': step}

        # записываем обновленные данные по сессии
        await self.systems.mc.set(chat_id, key, cfg.app.constants.timeout_for_chat)
        # возвращаем результат для тестирования навыка
        print(step)
        return step
