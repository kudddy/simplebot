import logging

from aiohttp.web_response import Response
from aiohttp_apispec import docs

from .base import BaseView
from message_schema import Updater

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class GetMessageFromTlg(BaseView):
    URL_PATH = r'/tlg/'

    @docs(summary="Endpoint для получения обновлений  с серверов телеграмма", tags=["Basic methods"],
          description="Endpoint для получения обновлений  с серверов телеграмма",
          )
    # @response_schema(PredictImageResp(), description="Возвращаем ранее добавлены комментарии к фотографии, "
    #                                                  "сортированные по дате")
    async def post(self):

        data: dict = await self.request.json()

        log.info("Message: %s", data)

        try:

            message = Updater(**data)

            await self.stage.next(message)

        except Exception as e:
            log.info("Message: %s with error %s", data, e)

        return Response(status=200, text="ok")
