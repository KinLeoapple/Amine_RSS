import asyncio
import time
from threading import Thread, Event

import nest_asyncio

from core.rss import RSS

nest_asyncio.apply()


class RssIntervalScheduler:
    __slots__ = ("tasks", "loop", "_event")

    def __init__(self):
        self.tasks = []
        self.loop = asyncio.new_event_loop()
        self._event = Event()
        thread = Thread(target=self.__start_loop, args=(self._event,))
        thread.start()

    def __start_loop(self, event):
        async def lock():
            while not event.is_set():
                await asyncio.sleep(1)

        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(asyncio.gather(lock()))

    def run_job(self, job: tuple, update_dir: str):
        self.tasks.append(job)
        asyncio.run_coroutine_threadsafe(self.__create_job(job, update_dir), self.loop)

    async def __create_job(self, job: tuple, update_dir: str):
        job = list(job)
        offset = int(time.time()) - int(job[2])
        if offset > int(job[3]) and int(job[4]) != 1:
            rss = RSS()
            rss.update(job[0], update_dir)
            rss.close()
        await asyncio.sleep(offset)
        self.run_job(tuple(job), update_dir)

    def shutdown(self):
        self._event.set()
