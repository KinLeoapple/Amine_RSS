import asyncio
import sys
import time
from threading import Thread
from typing import Union

import aria2p
import nest_asyncio
from tabulate import tabulate

# aria2
from aria2.init_aria2 import InitAria2

nest_asyncio.apply()
InitAria2()


def show_cli():
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    while True:
        downloads = []
        active_downloads = aria2.client.call("aria2.tellActive")
        waiting_downloads = aria2.client.call("aria2.tellWaiting", params=[0, sys.maxsize])
        stopped_downloads = aria2.client.call("aria2.tellStopped", params=[0, sys.maxsize])
        downloads.extend(active_downloads)
        downloads.extend(waiting_downloads)
        downloads.extend(stopped_downloads)

        download_info = []
        for download in downloads:
            # json_data = json5.dumps(download)
            for file in download["files"]:
                arr = str(file["path"]).split("/")
                name = arr[len(arr) - 1]
                try:
                    process = str(round(int(file["completedLength"]) / int(file["length"]) * 100, 2)) + "%"
                except ZeroDivisionError:
                    process = "0.00%"
                download_info.append([download["gid"], name, download["status"], process])
        print(tabulate(download_info, headers=["ID", "Name", "Status", "Progress"]), end="\n\n")
        time.sleep(10)


thread = Thread(target=show_cli)
thread.start()


class Task:
    __slots__ = ("aria2_path", "out_dir", "urls", "is_success", "failed_list")

    def __init__(self, urls: Union[str, list], out_dir: str):
        self.out_dir = out_dir
        self.urls: str = urls
        self.is_success = False
        self.failed_list = []
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if isinstance(urls, list):
            tasks = []
            for url in urls:
                tasks.append(self.__task(url))
            loop.run_until_complete(asyncio.gather(*tasks))
        elif isinstance(urls, str):
            loop.run_until_complete(asyncio.gather(self.__task(urls)))

    async def __task(self, url):
        aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret=""
            )
        )
        aria2.add(url, {"dir": self.out_dir})


class Aria2:
    __slots__ = "size"

    def __init__(self, size=3):
        self.size = size

    def get(self, urls: Union[str, list], out_dir: str):
        out_dir = out_dir.rstrip("/").rstrip("\\")
        # if url is a list
        if isinstance(urls, list):
            chunks = [urls[i:i + self.size] for i in range(0, len(urls), self.size)]
            for chunk in chunks:
                Task(chunk, out_dir)
        else:
            Task(urls, out_dir)
