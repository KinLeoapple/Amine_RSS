import os
import sqlite3
import time

import nest_asyncio
import requests
from tabulate import tabulate

from core import aria2
from core.methods import random_user_agent
from core.web import spider

nest_asyncio.apply()


class RssDB:
    __slots__ = ("conn", "cur")

    def __init__(self):
        self.conn = sqlite3.connect("rss.db")
        self.cur = self.conn.cursor()

        sql_table = '''CREATE TABLE IF NOT EXISTS rss
           (name TEXT,
            link TEXT,
            update_time NUMBER,
            interval NUMBER
            pause BOOLEAN);'''
        self.cur.execute(sql_table)

    def insert_one(self, name: str, link: str, interval: int, force):
        if not force:
            query = "SELECT * FROM rss WHERE link=?"
            self.cur.execute(query, (link,))
            result = self.cur.fetchone()
            if result is None:
                query = "INSERT INTO rss VALUES(?, ?, ?, ?, ?)"
                self.cur.execute(query, (name, link, 0, interval, False,))
                self.conn.commit()
        else:
            query = "DELETE FROM rss WHERE link=?"
            self.cur.execute(query, (link,))
            self.conn.commit()
            query = "INSERT INTO rss VALUES(?, ?, ?, ?, ?)"
            self.cur.execute(query, (name, link, 0, interval, False,))
            self.conn.commit()

    def remove_one(self, name: str):
        query = "DELETE FROM rss WHERE name=?"
        self.cur.execute(query, (name,))
        self.conn.commit()

    def update_one(self, name: str, link: str, update_time: int, interval: int):
        query = "UPDATE rss SET name=?, link=?, update_time=?, interval=? WHERE name=?"
        self.cur.execute(query, (name, link, update_time, interval, name,))
        self.conn.commit()

    def set_pause(self, name: str):
        query = "UPDATE rss SET pause=? WHERE name=?"
        self.cur.execute(query, (True, name,))
        self.conn.commit()

    def set_resume(self, name: str):
        query = "UPDATE rss SET pause=? WHERE name=?"
        self.cur.execute(query, (False, name,))
        self.conn.commit()

    def fetch_one(self, name: str):
        query = "SELECT * FROM rss WHERE name=?"
        self.cur.execute(query, (name,))
        return self.cur.fetchone()

    def fetch_all(self):
        query = "SELECT * FROM rss"
        self.cur.execute(query)
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()


class RSS:
    __slots__ = "rss_db"

    def __init__(self):
        self.rss_db = RssDB()

    def close(self):
        self.rss_db.close()

    def add(self, name: str, link: str, interval: int, force=False):
        self.rss_db.insert_one(name, link, interval, force)

    def remove(self, name: str):
        self.rss_db.remove_one(name)

    def show(self, name: str):
        data = self.rss_db.fetch_one(name)
        if data is None:
            data = ("None", "None", "None", "None", "None",)
        print(
            tabulate([map(lambda x: str(x), list(data))], headers=["Name", "Link", "Update Time", "Interval", "Pause"]))
        return data

    def show_all(self):
        data = self.rss_db.fetch_all()
        if len(data) <= 0:
            data.append(("None", "None", "None", "None", "None",))
        print(tabulate(map(lambda y: list(y), data), headers=["Name", "Link", "Update Time", "Interval", "Pause"]))
        return data

    def pause_one(self, name: str):
        self.rss_db.set_pause(name)

    def pause_all(self):
        data = self.rss_db.fetch_all()
        if len(data) > 0:
            for dt in data:
                dt = list(dt)
                self.pause_one(dt[0])

    def resume_one(self, name: str):
        self.rss_db.set_resume(name)

    def resume_all(self):
        data = self.rss_db.fetch_all()
        if len(data) > 0:
            for dt in data:
                dt = list(dt)
                self.resume_one(dt[0])

    def update(self, name: str, update_dir: str):
        aria2_client = aria2.Aria2()
        update_dir = update_dir.rstrip("/").rstrip("\\")
        data = self.rss_db.fetch_one(name)
        if data is not None:
            data = list(data)
            url = data[1]
            self.__call_aria2(aria2_client, data, url, update_dir)

    def update_all(self, update_dir: str):
        aria2_client = aria2.Aria2()
        update_dir = update_dir.rstrip("/").rstrip("\\")
        data = self.rss_db.fetch_all()
        if len(data) > 0:
            for dt in data:
                dt = list(dt)
                url = dt[1]
                self.__call_aria2(aria2_client, dt, url, update_dir)

    def __call_aria2(self, aria2_client, data: list, url: str, update_dir: str):
        # find rss file
        r = requests.get(url, headers=random_user_agent())
        selector = spider.HtmlSelector(r.content.decode("utf-8"))
        r.close()
        torrents = []
        # get torrent url
        for i in selector.select("enclosure"):
            torrent = i["url"].strip("'").strip("\"")
            torrents.append(torrent)
        base_path = update_dir + os.sep + data[0]
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        # download with aria2
        aria2_client.get(torrents, base_path)
        # update database info
        self.rss_db.update_one(data[0], data[1], int(time.time()), data[3])
