import asyncio
import os
import sys
import time
from threading import Event, Thread
from typing import Union

import nest_asyncio

from aria2 import aria2_client

nest_asyncio.apply()


class Aria2Methods:
    __slots__ = ("event", "client")

    def __init__(self):
        self.event = None
        self.client = aria2_client.client

    def get_all_downloads(self):
        downloads = []
        active_downloads = self.client.tell_active()
        waiting_downloads = self.client.tell_waiting(0, sys.maxsize)
        stopped_downloads = self.client.tell_stopped(0, sys.maxsize)
        downloads.extend(active_downloads)
        downloads.extend(waiting_downloads)
        downloads.extend(stopped_downloads)
        return downloads

    def do_clean_up(self, name, status, path, download):
        # remove torrent file if download process is complete
        if name.lower().endswith(".torrent") and \
                status.lower() != "active" and \
                status.lower() != "waiting" and \
                status.lower() != "paused":
            # remove file if it exists
            if os.path.exists(path):
                os.remove(path)
                self.__remove_download_result(download)
        # other types of files will directly remove from download results
        else:
            self.__remove_download_result(download)

    def __remove_download_result(self, download):
        # if download is completed
        if str(download["status"]).lower() == "complete":
            self.client.remove_download_result(download["gid"])
        # if error code is 12, which means downloading the same file
        # if error code is 13, which means the file has already downloaded
        if str(download["status"]).lower() == "error":
            if int(download["errorCode"]) == 12 or int(download["errorCode"]) == 13:
                self.client.remove_download_result(download["gid"])

    def auto_clean_up(self):
        self.event = Event()

        def run():
            while not self.event.is_set():
                self.clean_up()
                time.sleep(1)

        thread = Thread(target=run)
        thread.start()

    def stop_auto_clean_up(self):
        if self.event is not None:
            self.event.set()
            self.event = None

    def clean_up(self):
        downloads = self.get_all_downloads()
        for download in downloads:
            for file in download["files"]:
                arr = str(file["path"]).split("/")
                name = arr[len(arr) - 1]
                self.do_clean_up(name, str(download["status"]), str(file["path"]), download)


class Task:
    __slots__ = ("aria2_path", "out_dir", "urls", "gids")

    def __init__(self, urls: Union[str, list], out_dir: str):
        self.out_dir = out_dir
        self.urls: str = urls
        self.gids: list = []
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
        download = aria2_client.client.add_uri([url], options={"dir": self.out_dir})
        self.gids.append(download)


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

    @staticmethod
    def get_download_info():
        downloads = Aria2Methods().get_all_downloads()

        info = []
        for download in downloads:
            for file in download["files"]:
                arr = str(file["path"]).split("/")
                name = arr[len(arr) - 1]
                try:
                    process = str(round(int(file["completedLength"]) / int(file["length"]) * 100, 2)) + "%"
                except ZeroDivisionError:
                    process = str(round(0)) + "%"
                info.append({"id": download["gid"], "name": name, "status": download["status"], "process": process})
                Aria2Methods().do_clean_up(name, str(download["status"]), str(file["path"]), download)
        return info

    @staticmethod
    def get_aria2():
        return aria2_client
