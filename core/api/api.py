import asyncio
from threading import Thread

import nest_asyncio
from quart import Quart, websocket, request
from hypercorn.config import Config
from hypercorn.asyncio import serve


from core import files, aria2
from core.files import VideoCover
from core.methods import methods
from core.rss import RSS

nest_asyncio.apply()

app = Quart(__name__)
rss = RSS()


class API:
    __slots__ = "app"

    def __init__(self):
        self.app = app

    def get_app(self):
        return self.app

    def start(self):
        asyncio.run(serve(self.app, Config()))

    """
    for files
    """

    @staticmethod
    @app.websocket("/files")
    async def ws_files():
        await websocket.send_json({"OK": "OK"})
        while True:
            try:
                path = await websocket.receive()
                file_list = files.Files(path).get_files()
                await websocket.send_json({"files": file_list})
            except Exception as err:
                print(err)
                await websocket.send_json({"err": "error"})

    @staticmethod
    @app.route("/file_cover/", methods=["POST"])
    async def file_cover():
        data = await request.get_json()
        path = data["path"]
        base64_img = VideoCover(path).get_base64_img()
        return base64_img

    """
    for downloads
    """

    @staticmethod
    @app.websocket("/downloads")
    async def ws_downloads():
        await websocket.send_json({"OK": "OK"})
        while True:
            try:
                info = aria2.Aria2Methods().get_all_downloads()
                if len(info) > 0:
                    await websocket.send_json({"downloads": info})
                await asyncio.sleep(1)
            except Exception as err:
                print(err)
                await websocket.send_json({"err": "error"})

    """h
    for download rules
    """

    @staticmethod
    @app.route("/get_rule/", methods=["POST"])
    async def get_rule():
        data = await request.get_json()
        name = data["name"]
        return rss.get(name)

    @staticmethod
    @app.route("/get_all_rules/", methods=["POST"])
    async def get_all_rules():
        return rss.get_all()

    @staticmethod
    @app.route("/set_rule/", methods=["POST"])
    async def set_rule():
        data = await request.get_json()
        name = data["name"]
        is_pause = data["is_pause"]
        if int(is_pause) == 0:
            rss.resume_one(name)
            return "1"
        elif int(is_pause) == 1:
            rss.pause_one(name)
            return "1"
        else:
            return "0"

    @staticmethod
    @app.route("/add_rule/", methods=["POST"])
    async def add_rule():
        data = await request.get_json()
        name = data["name"]
        url = data["url"]
        interval = data["interval"]
        is_force = data["is_force"]
        is_add = rss.add(name, url, interval, is_force)
        if is_add:
            return "1"
        else:
            return "0"

    @staticmethod
    @app.route("/remove_rule/", methods=["POST"])
    async def remove_rule():
        data = await request.get_json()
        name = data["name"]
        rss.remove(name)
        return "0"

