# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import logging

from aiohttp_requests import requests
from ...plugins.core.config import setting

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


def timing(f):
    def wrap(*args, **kwargs):
        start = time.time()
        ret = f(*args, **kwargs)
        end = time.time()
        log.debug('{:s} function took {:.3f} ms'.format(f.__name__, (end - start) * 1000.0))
        return ret

    return wrap


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
















