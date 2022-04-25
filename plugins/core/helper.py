# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import sys
import logging
import aiohttp
from collections import defaultdict, Iterable

import html2text
from aiohttp_requests import requests
from plugins.core.config import setting

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


def generate_message_body(vacancy_info: dict, message_size: int = 500) -> str:
    """
    Генерируем сообщение для отправки
    :param vacancy_info: информация по вакансии
    :param message_size: дилина сообщения, по дефолту 500
    :return: возвращает готовую строку для отправки
    """
    title: str = "💥 Название позиции: " + vacancy_info['title'] + '\n'
    description: str = title + "💥 Описание: " + html2text.html2text(vacancy_info['header'])[
                                                 :message_size] + "..." + '\n'
    message_body: str = description + '\n' "Показать еще❓"
    return message_body


async def send_message(url: str,
                       chat_id: int,
                       text: str,
                       parse_mode: str = None,
                       buttons: list or None = None,
                       inline_keyboard: list or None = None,
                       one_time_keyboard: bool = True,
                       resize_keyboard: bool = True,
                       remove_keyboard: bool = False):
    payload = {
        "chat_id": chat_id,
        "text": text[:4095],
        "reply_markup": {
            "remove_keyboard": remove_keyboard
        }
    }

    if parse_mode:
        payload.update({"parse_mode": parse_mode})

    if buttons:
        # TODO hardcode
        keyboards = [[{"text": text}] for text in buttons]
        payload["reply_markup"].update({
            "keyboard": keyboards,
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard
        })

    if inline_keyboard:
        payload["reply_markup"].update({"inline_keyboard": inline_keyboard})

    headers = {
        "Content-Type": "application/json"
    }

    response = await requests.get(url, headers=headers, data=json.dumps(payload), ssl=False)

    response = await response.json()

    res = response.get("ok")

    # маскирование текста
    payload["text"] = "*******"

    if res:
        log.debug("request with payload: %s success delivered to tlg", payload)
    else:
        log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)


async def edit_message(url: str,
                       text: str,
                       chat_id: int or str = None,
                       message_id: int = None,
                       inline_keyboard: list or None = None,
                       inline_message_id: str = None,
                       parse_mode: str = None,
                       entities: str = None,
                       disable_web_page_preview: bool = None,
                       ):
    payload = {
        "text": text[:4095]
    }
    if chat_id:
        payload.update({"chat_id": chat_id})
    if message_id:
        payload.update({"message_id": message_id})
    if parse_mode:
        payload.update({"parse_mode": parse_mode})

    headers = {
        "Content-Type": "application/json",
    }

    if inline_keyboard:
        payload.update(
            {"reply_markup": {
                "inline_keyboard": inline_keyboard}
            })

    response = await requests.get(url, headers=headers, data=json.dumps(payload), ssl=False)

    response = await response.json()

    res = response.get("ok")

    payload["text"] = "*******"

    if res:
        log.debug("request with payload: %s success delivered to tlg", payload)
    else:
        log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)


async def send_animation(url: str, chat_id: int, file_id: str):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "chat_id": chat_id,
        "animation": file_id
    }

    response = await requests.get(url, headers=headers, data=json.dumps(payload), ssl=False)
    response = await response.json()
    res = response.get("ok")

    if res:
        log.debug("request with payload: %s success delivered to tlg", payload)
    else:
        log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)


async def send_video(url: str, chat_id: int, file_id: str):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "chat_id": chat_id,
        "video": file_id
    }

    response = await requests.get(url, headers=headers, data=json.dumps(payload), ssl=False)
    response = await response.json()
    res = response.get("ok")

    if res:
        log.debug("request with payload: %s success delivered to tlg", payload)
    else:
        log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)


async def get_file_path(file_id: str) -> str:
    url = setting.app.hosts.tlg.get_file_path.format(file_id)
    response = await requests.get(url, ssl=False)
    response = await response.json()

    return response.get("result", {}).get("file_path", False)


async def get_file(file_path: str) -> object:
    url = setting.app.hosts.tlg.get_file.format(file_path)
    response = await requests.get(url, ssl=False)
    response = await response.json()
    # TODO получить octstream file
    return


async def push_to_queue(file: str) -> str:
    url = "https://hf.space/gradioiframe/akhaliq/AnimeGANv2/api/queue/push/"
    data = {"data": ["data:image/jpeg;base64,{}".format(file)], "action": "predict"}
    response = await requests.get(url, ssl=False)
    response = await response.json()


async def generate_auth_message(url: str, vacancy_id: int) -> str:
    log.debug("we requesting auth user message")
    auth = aiohttp.BasicAuth(setting.app.pwd.sf.us, setting.app.pwd.sf.ps)

    response = await requests.get(url.format(vacancy_id),
                                  auth=auth,
                                  ssl=False)
    d = await response.json()

    podr = "Подразделение: {}".format(d['d'].get("custsourcerTeam", "Нет"))
    intr = "Интервьюр: {}".format(d['d'].get("custInterviewers", "Нет"))
    max_zp = "Максимальная зп: {}".format(d['d'].get("salaryMax", "Нет"))
    min_zp = "Минимальная зп: {}".format(d['d'].get("salaryMin", "Нет"))
    block = "Блок: {}".format(d['d'].get("division", "Нет"))
    bonus = "Бонус: {}".format(d['d'].get("bonusAmount", "Нет"))
    vlk = "Вилка: {}".format(d['d'].get("custSalarySmart", "Нет"))
    location = "Локация: {}".format(d['d'].get("custCity", "Нет"))
    pos_name = "Название должности: {}".format(d['d'].get("custTitle", "Нет"))
    year_average = "Годовой доход: {}".format(d['d'].get("custAverageYear", "Нет"))
    time = "Сколько ищут? {} дней".format(d['d'].get("age", "Нет"))

    result = podr + '\n' + intr + '\n' + max_zp + '\n' + min_zp + '\n' + block + '\n' + bonus + '\n' + vlk + '\n' + location + '\n' + pos_name + '\n' + year_average + '\n' + time + '\n'

    return result


def escape_markdown(text: str, version: int = 1, entity_type: str = None) -> str:
    """
    Helper function to escape telegram markup symbols.
    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if int(version) == 1:
        escape_chars = r'_*`['
    elif int(version) == 2:
        if entity_type in ['pre', 'code']:
            escape_chars = r'\`'
        elif entity_type == 'text_link':
            escape_chars = r'\)'
        else:
            escape_chars = r'_*[]()~`>#+-=|{}.!'
    else:
        raise ValueError('Markdown version must be either 1 or 2!')

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


# class GetVac:
#     def __init__(self, vacs_filename):
#         self.vacs = pcl.get_pickle_file(vacs_filename)
#
#     def get_vac_by_id(self, key: int):
#         if key in self.vacs.keys():
#             return self.vacs[key]
#         else:
#             return False
#
#     def update_cache(self, new_cache):
#         self.vacs = new_cache


############## ф-ции общего назначения

class Coder:
    @staticmethod
    def encode(obj: object):
        return json.dumps(obj).encode()

    @staticmethod
    def decode(byte: bytes):
        return json.loads(byte.decode())


def split_dict_equally(input_dict, chunks=2):
    """
    Разделение словаря на n частей. Возвращает лист из словарей.
    Аrgs:
        type(dict) - input_dict : словарь с любым типом данных
        type(int) - chunks : размер выходного списка
    Returns:
        type(list) - return_list : список с словарями
    """
    # prep with empty dicts
    return_list = [dict() for idx in range(chunks)]
    idx = 0
    for k, v in input_dict.items():
        return_list[idx][k] = v
        if idx < chunks - 1:  # indexes start at 0
            idx += 1
        else:
            idx = 0
    return return_list


def func(*dicts):
    """
    Объединяет словари по ключа. Работает только со строками
    Аrgs:
        type(dict) - input_dict : словари
    Returns:
        type(list) - return_list : список с словарями
    """
    keys = set().union(*dicts)
    return {k: " ".join(dic.get(k, '') for dic in dicts) for k in keys}


def check_updates(recs_new, recs_old):
    """
    В случае если старые и новые рекомендации разные,то возвращаем True, если же одинаковые то
    False
    Аrgs:
        type(list) - recs_new : список с новыми рекомендациями
        type(list) - recs_old : строка c sf_id
    Returns:
        type(list) - jc : список с актуальными jc
    """
    len_intersect = len(set(recs_old).intersection(set(recs_new)))

    len_old_rec = len(recs_old)

    if len_intersect == len_old_rec and recs_old == recs_new:
        return False
    else:
        return True


def get_score(recs_new):
    """
    Ф-ция возвращает искуственно созданных скор для рекомендаций в зависимости от кол-ва новых рекомендаций
    Аrgs:
        type(list) - recs_new : список с новыми рекомендациями
    Returns:
        type(list) - score : список со скором
    """
    len_recs = len(recs_new)
    min_trash = 0.6
    max_trash = 0.95
    score = []
    error = 0
    for i in range(len(recs_new)):
        error += (max_trash - min_trash) / len_recs
        score.append(str(max_trash - error))
    return score


def group_by_value(dct):
    """
    Группируем ключ по значениям
    Аrgs:
        type(dict) - input_dict : словарь с любым типом данных
        type(int) - chunks : размер выходного списка
    Returns:
        type(list) - return_list : список с словарями
    """
    v = {}
    for key, value in sorted(dct.items()):
        v.setdefault(value, []).append(key)
    return v


def group_tuples_by_key(tuples):
    """
    Ф-ция возвращает сгруппированный по ключу словарь
    Аrgs:
        type(list((key,val),(key,val))) - tuples : список с кортежами
    Returns:
        type(dict) - score : сгруппированный по ключу словарь
    """
    d = defaultdict(list)
    for k, *v in tuples:
        d[k].append(v[0])
    b = list(d.items())
    return dict(b)


def add_list(main_list, new_list):
    """
    Ф-ция добавляет в начала списка main_list список new_list
    Аrgs:
        type(list) - main_list : основной список с элементами
        type(list) - bad_list : список элементов, которые нужно удалить из основного списка
    Returns:
        type(list) - new_list : новый список
    """
    return new_list + main_list


def diff_no_mutation(main_list, bad_list):
    """
    Ф-ция возвращает список элементов main_list которых нет в bad_list
    Аrgs:
        type(list) - main_list : основной список с элементами
        type(list) - bad_list : список элементов, которые нужно удалить из основного списка
    Returns:
        type(list) - clean_list : очищенный список
    """
    clean_list = [x for x in main_list if x not in bad_list]
    return clean_list


def drop_dublicates_list(seq):
    """
    Удаляем дубликаты из списка
    Аrgs:
        type(list) - seq : основной список с элементами
    Returns:
        type(list) - clean_list : список без дубликатов
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def chunks(array, chunk_size):
    """
    Ф-ция возвращает сгруппированный по ключу словарь. Ф-цию нужно обернуть в list()
    Аrgs:
        type(list)- array : список
        type(int) - chunk_size : коэф от которого зависит какой размер батча
    Returns:
        n/a
    """
    for i in range(0, len(array), chunk_size):
        yield array[i:i + chunk_size]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class safesub(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def sub(text):
    return text.format_map(safesub(sys._getframe(1).f_locals))


def flatten(items, ignore_types=(str, bytes)):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from (flatten(x))
        else:
            yield x


def structure_normalization(d: list) -> dict:
    """
    Нормализация структуры данных, которая приходит из JobApi
    :param d:
    :return:
    """
    local_dict = {}
    for k in d:
        local_dict.update({k['id']: k})
    return local_dict


def remove_html_in_dict(text):
    html_pattern = re.compile('<.*?>')
    title_pattern = re.compile(r'([a-zа-я](?=[A-ZА-Я])|[A-ZА-Я](?=[A-ZА-Я][a-zа-я]))')

    val = title_pattern.sub(r'\1 ', html_pattern.sub(r'', text).replace('\xa0', ' '))
    text = re.sub(r'&[\w]*;', ' ', val).strip()
    return text


def get_clean_text_str(text_vacs: dict) -> str:
    """
    Ф-ция необходима для процедуры токенизации. Преобразует данные из словаря в единую строку
    :param text_vacs: словарь с описанием вакансии
    :return: единая строка содержащая в себе поля
    """
    if 'title' in text_vacs.keys():
        title = remove_html_in_dict(text_vacs['title'])
    else:
        title = 'fail'

    # обязанности
    if 'duties' in text_vacs.keys():
        duties_text = remove_html_in_dict(text_vacs['duties'])
    else:
        duties_text = 'fail'

    # условия
    if 'conditions' in text_vacs.keys():
        # conditions_text = remove_html_in_dict(text_vacs['conditions'])
        conditions_text = 'fail'
    else:
        conditions_text = 'fail'

    return title + ' ' + duties_text


def model_result(input_vector: dict, token: str, url: str) -> list:
    url = url + 'get_recs'

    data = {
        'token': token,
        'vector': input_vector
    }
    result = get_response(url, data)
    if result['status'] == 'ok':
        result = result['result']
    else:
        result = []

    return result


def search_result(text: str, token: str, url: str) -> list:
    url = url + 'search'

    data = {
        'token': token,
        'string': text
    }
    result = get_response(url, data)
    if result['status'] == 'ok':
        result = result['result']
    else:
        result = []

    return result


def get_response(url, data):
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    payload = json.dumps(data)
    r = requests.post(url, data=payload, headers=headers)
    result = r.json()
    return result


def get_nearest_vac(url: str, city: str):
    data = {
        "token": "shdfksdhflkdsfh",
        "data": city,
        "get_vac": True
    }
    nearest_vac = get_response(url, data)

    status = nearest_vac['status']

    if status:
        return nearest_vac['data']
    else:
        return -1
