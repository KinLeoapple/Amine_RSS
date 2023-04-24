import asyncio
from typing import Union

import nest_asyncio

# aria2
from aria2.init_aria2 import InitAria2

nest_asyncio.apply()


class Task:
    __slots__ = ("aria2_path", "out_dir", "urls", "is_success", "failed_list")

    def __init__(self, aria2_path: str, urls: Union[str, list], out_dir: str):
        self.aria2_path: str = aria2_path
        self.out_dir = out_dir
        self.urls: str = urls
        self.is_success = False
        self.failed_list = []
        loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(loop)
        if isinstance(urls, list):
            tasks = []
            for url in urls:
                tasks.append(self.__task(url))
            loop.run_until_complete(asyncio.gather(*tasks))
        elif isinstance(urls, str):
            loop.run_until_complete(asyncio.gather(self.__task(urls)))

    async def __task(self, url):
        process = await asyncio.create_subprocess_exec(
            self.aria2_path, "--seed-time=0",
            "-d", self.out_dir, "-x", "16", "-s", "16", "-k", "10M", url)
        await process.communicate()


class Aria2:
    __slots__ = ("aria2_path", "size")

    def __init__(self, size=3):
        self.aria2_path = InitAria2().get_aria2_path()
        self.size = size

    def get(self, urls: Union[str, list], out_dir: str):
        out_dir = out_dir.rstrip("/").rstrip("\\")
        # if url is a list
        if isinstance(urls, list):
            chunks = [urls[i:i + self.size] for i in range(0, len(urls), self.size)]
            for chunk in chunks:
                Task(self.aria2_path, chunk, out_dir)
        else:
            Task(self.aria2_path, urls, out_dir)
