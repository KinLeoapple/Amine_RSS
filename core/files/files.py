"""
For openCV-python please use
"pip install opencv-python"
"""
import asyncio
import base64
import os.path
import sqlite3
from io import BytesIO
import atexit

import nest_asyncio
import numpy as np
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from numba import jit

nest_asyncio.apply()


class CoverDB:
    __slots__ = ("conn", "cur")

    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()

        sql_table = '''CREATE TABLE IF NOT EXISTS cover
                   (path TEXT,
                    base64_img TEXT);'''
        self.cur.execute(sql_table)

    def fetch(self, path: str):
        query = "SELECT * FROM cover WHERE path=?"
        self.cur.execute(query, (path,))
        result = self.cur.fetchone()
        return result

    def fetch_all(self):
        query = "SELECT * FROM cover"
        self.cur.execute(query)
        return self.cur.fetchall()

    def append(self, path: str, base64_img: str):
        if self.fetch(path) is not None:
            self.remove(path)
        query = "INSERT INTO cover VALUES(?, ?)"
        self.cur.execute(query, (path, base64_img,))
        self.conn.commit()

    def batch_remove(self):
        data = self.fetch_all()
        for file in data:
            if not os.path.exists(file[0]):
                self.remove(file[0])

    def remove(self, path: str):
        query = "DELETE FROM cover WHERE path=?"
        self.cur.execute(query, (path,))
        self.conn.commit()

    def compares(self):
        query = "VACUUM;"
        self.cur.execute(query)

    @atexit.register
    def close(self):
        self.cur.close()
        self.conn.close()


class VideoCover:
    __slots__ = ("path", "compress_rate", "cache")

    def __init__(self, path, compress_rate=0.8, cache=True):
        self.path = path
        self.compress_rate = compress_rate
        self.cache = cache

    def get_base64_img(self):
        db = CoverDB()
        result = db.fetch(self.path)
        if result is not None:
            data = list(result)
            base64_img = data[1]
        else:
            pil_img = self.__get_pil_cover(self.path)
            base64_img = self.__pil_base64(pil_img)
            if self.cache:
                self.__cache(base64_img, db)
        db.close()
        return base64_img

    def __cache(self, base64_img, db):
        db.append(self.path, base64_img)
        db.compares()

    @jit(parallel=True)
    def __get_pil_cover(self, video_path):
        video = VideoFileClip(video_path)
        clip_frame_time = video.duration / 3
        img_array = video.make_frame(t=clip_frame_time)
        image = Image.fromarray(np.uint8(img_array))
        w, h = image.size
        resize_image = image.resize((int(w * self.compress_rate), int(h * self.compress_rate)))
        return resize_image

    @jit(parallel=True)
    def __pil_base64(self, image):
        img_buffer = BytesIO()
        image.save(img_buffer, format="JPEG")
        byte_data = img_buffer.getvalue()
        base64_str = base64.b64encode(byte_data)
        return base64_str


class Files:
    __slots__ = ("path", "file_list")

    def __init__(self, path):
        self.file_list = None
        self.path = path

    def get_files(self):
        db = CoverDB()
        self.file_list: list = []
        if os.path.exists(self.path):
            if os.path.isfile(self.path):
                root = os.path.dirname(self.path)
                filename = os.path.basename(self.path)
                self.__append_file(root, filename)
            else:
                self.__walk_dir()
            db.batch_remove()
            db.close()
            return self.file_list
        else:
            db.batch_remove()
            db.close()
            return []

    def clean_torrent_files(self):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if filename.lower().endswith(".torrent"):
                    os.remove(os.path.join(root, filename))

    def __walk_dir(self):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if not filename.lower().endswith(".torrent") and \
                        not filename.lower().endswith(".aria2"):
                    self.__append_file(root, filename)

    def __append_file(self, root, file_name):
        self.file_list.append({"root": os.path.join(root, "").replace("\\\\", "/").replace("\\", "/"),
                               "name": file_name})

