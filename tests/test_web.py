from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import logging

from plugins.core.start import Updater

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


def generate_payload(text: str):
    return {
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
            "text": text
        }
    }


class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        return Updater._create_app_hook()

    @unittest_run_loop
    async def test_step_one(self):
        async with self.client.request("POST", "/tlg/", json=generate_payload("подарок")) as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            print(text)
        self.assertIn("ok", text)

    @unittest_run_loop
    async def test_step_two(self):
        async with self.client.request("POST", "/tlg/", json=generate_payload("подарок")) as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            print(text)
        self.assertIn("ok", text)
