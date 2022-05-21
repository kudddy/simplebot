import logging
from threading import Thread

from prometheus_client import Summary

from ..plugins.core.helper import timing
from ..plugins.core.start import Updater


app = Updater()


# starts thread with telegram workers, who send logs to the consumers
tgl_thread = Thread(target=app.run_pulling)
tgl_thread.start()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Метод handlers. Этот метод будет вызываться при вызове функции
@REQUEST_TIME.time()
@timing
def handler(request):

    resp = {
        "status": True
    }

    return (
        resp
        ,
        200,
        {"Content-Type": "application/json"})

# Раскомментируйте и измените этот метод, если вам нужен кастомный HealthCheck
# def health():
#     return True, "Custom healthcheck"
