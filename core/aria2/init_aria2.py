"""
aria2 version: 1.36.0
"""
import asyncio
import os.path
import secrets
import shutil
import zipfile
from threading import Thread

import aria2p
import nest_asyncio
import requests

from core import methods

nest_asyncio.apply()


class InitAria2:
    __slots__ = ("aria2_path", "base_path", "session_path", "aria2", "port", "secret")

    def __init__(self):
        self.secret = secrets.token_urlsafe()
        self.__check_aria2()
        self.port = methods.get_port()
        thread = Thread(target=self.__run_aria2)
        thread.start()

        self.aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=self.port,
                secret=self.secret
            )
        )

    def __check_aria2(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        self.base_path = dirname + os.sep + "aria2" + os.sep
        self.session_path = self.base_path + "aria2.session"
        current_os = methods.get_os()
        if current_os == "nt":
            self.aria2_path = self.base_path + "aria2c.exe"
        elif current_os == "posix":
            self.aria2_path = self.base_path + "aria2c"

        if not os.path.exists(self.aria2_path):
            os.makedirs(self.base_path)
            self.__download_aria2()

    def __run_aria2(self):
        async def run():
            process = await asyncio.create_subprocess_exec(
                self.aria2_path,
                "--seed-time=0",
                "--enable-rpc",
                "--rpc-listen-all",
                f"--rpc-listen-port={self.port}",
                f"--rpc-secret={self.secret}",
                "--bt-require-crypto=true",
                f"--input-file={self.session_path}",
                f"--save-session={self.session_path}",
                "--save-session-interval=60",
                "--force-save=true",
                "--continue=true",
                "--lowest-speed-limit=0",
                "--disable-ipv6=true",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            await process.communicate()

        if not os.path.exists(self.session_path):
            f = open(self.session_path, mode="w")
            f.write("")
            f.close()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(run()))

    def get_aria2_path(self):
        return self.aria2_path

    def get_aria2(self):
        return self.aria2

    """
        for linux: https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-aarch64-linux-android-build1.zip
        for windows: https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip
    """

    def __download_aria2(self):
        current_os = methods.get_os()
        url = ""
        if current_os == "nt":
            url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip"
        elif current_os == "posix":
            url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-aarch64-linux-android-build1.zip"

        r = requests.get(url)
        temp_path = self.base_path + "temp"
        f = open(temp_path, mode="wb")
        f.write(r.content)
        f.close()

        zip_aria2 = zipfile.ZipFile(temp_path)
        zip_aria2.extractall(self.base_path)
        zip_aria2.close()

        extract_path = self.base_path + \
                       url.split("https://github.com/aria2/aria2/releases/download/release-1.36.0/")[1] \
                           .split(".zip")[0] + os.sep
        dir_list = os.listdir(extract_path)
        for file in dir_list:
            shutil.move(extract_path + file, self.base_path + file)
        os.rmdir(extract_path)

        os.remove(temp_path)

        r.close()
