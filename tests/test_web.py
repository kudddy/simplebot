from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
import logging

from plugins.core.start import Updater


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)

class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """

        # async def hello(request):
        #     return web.Response(text='Hello, world')
        #
        # app = web.Application()
        # app.router.add_get('/', hello)
        return Updater._create_app_hook()

    async def test_example(self):
        print("fsdfsdf")
        data = {
            "update_id": 243475549,
            "message": {
                "message_id": 9450,
                "from": {
                    "id": 81432612,
                    "is_bot": False,
                    "first_name": "Kirill",
                    "username": "kkkkk_kkk_kkkkk",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 81432612,
                    "first_name": "Kirill",
                    "username": "kkkkk_kkk_kkkkk",
                    "type": "private"
                },
                "date": 1589404439,
                "text": "Подарок"
            }
        }
        log.debug("dsdsfdsfs")
        async with self.client.request("POST", "/tlg/", json=data) as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            print(text)
        self.assertIn("Hello, world", text)
