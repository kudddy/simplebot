from asyncio import get_event_loop

from plugins.core.long_polling import run_loop

loop = get_event_loop()


loop.run_until_complete(run_loop())