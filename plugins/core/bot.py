import logging
import json
from time import sleep
from typing import Union

from asyncio import sleep

from pydantic import ValidationError

from plugins.core.message_schema import Updates

from aiohttp_requests import requests

import requests as req

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)

URL_SEND_MESSAGE = "https://api.telegram.org/bot{}/sendMessage"
URL_EDIT_MESSAGE = "https://api.telegram.org/bot{}/editMessageText"
URL_SEND_ANIMATION = "https://api.telegram.org/bot{}/sendAnimation"
URL_SEND_VIDEO = "https://api.telegram.org/bot{}/sendVideo"


class Retry:
    def __init__(self, retry=5, time_to_sleep=15):
        self._retry = retry
        self._count = 0
        self._time_to_sleep = time_to_sleep

    async def send(self, method: str,
                   url: str,
                   headers: dict):

        try:
            data = await requests.get(url,
                                      headers=headers,
                                      ssl=False)
            return data

        except req.exceptions.ConnectionError:

            log.info("problems with request, start retry")

            self._count += 1

            if self._retry > self._count:
                await sleep(self._time_to_sleep)
                return await self.send(method, url, headers)
            else:
                return -1


retry = Retry()


class Bot:
    def __init__(self, token):
        self.token = token

    async def send_message(self,
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

        response = await requests.get(URL_SEND_MESSAGE.format(self.token), headers=headers, data=json.dumps(payload),
                                      ssl=False)

        response = await response.json()

        res = response.get("ok")

        # маскирование текста
        payload["text"] = "*******"

        if res:
            log.debug("request with payload: %s success delivered to tlg", payload)
        else:
            log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)

    async def edit_message(self,
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

        response = await requests.get(URL_EDIT_MESSAGE.format(self.token),
                                      headers=headers,
                                      data=json.dumps(payload),
                                      ssl=False)

        response = await response.json()

        res = response.get("ok")

        payload["text"] = "*******"

        if res:
            log.debug("request with payload: %s success delivered to tlg", payload)
        else:
            log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)

    async def send_animation(self,
                             chat_id: int,
                             file_id: str):
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "chat_id": chat_id,
            "animation": file_id
        }

        response = await requests.get(URL_SEND_ANIMATION.format(self.token), headers=headers, data=json.dumps(payload),
                                      ssl=False)
        response = await response.json()
        res = response.get("ok")

        if res:
            log.debug("request with payload: %s success delivered to tlg", payload)
        else:
            log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)

    async def send_video(self, chat_id: int, file_id: str):
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "chat_id": chat_id,
            "video": file_id
        }

        response = await requests.get(URL_SEND_VIDEO.format(self.token), headers=headers, data=json.dumps(payload),
                                      ssl=False)
        response = await response.json()
        res = response.get("ok")

        if res:
            log.debug("request with payload: %s success delivered to tlg", payload)
        else:
            log.debug("request with payload: %s delivered to tlg with error: %s", payload, response)

    async def get_updates(self, offset: int) -> Union[Updates, int]:
        headers = {
            "Content-Type": "application/json"
        }
        # data = request("GET",
        #                f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}",
        #                headers=headers)

        data = await retry.send("GET",
                                f"https://api.telegram.org/bot{self.token}/getUpdates?offset={offset}",
                                headers=headers)

        if data == -1:
            log.warning("long timeout")
            return -1

        log.debug(f"bot with token - {self.token} gets update with status - {data.status}")

        if data.status == 200:
            try:
                data = await data.json()
                response = Updates(**data)
                return response
            except ValidationError as e:
                return -1
        else:
            try:
                log.info(
                    f"something wrong with bot - "
                    f"{self.token} gets update with status - "
                    f"{data.status} and payload - {await data.json()}"
                )
            except Exception as e:
                log.info(f"can't decode json from response, error - {str(e)}")
            return -1
