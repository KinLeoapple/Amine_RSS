import os
import zipfile

import requests

import methods


class InitChrome:
    __slots__ = ("chrome_path", "base_path")

    def __init__(self):
        self.__check_chrome()

    def __check_chrome(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        self.base_path = dirname + os.sep + "chrome" + os.sep
        current_os = methods.get_os()
        if current_os == "nt":
            self.chrome_path = self.base_path + "chromedriver.exe"
        elif current_os == "posix":
            self.chrome_path = self.base_path + "chromedriver"

        if not os.path.exists(self.chrome_path):
            os.makedirs(self.base_path)
            self.__download_chrome()

    def get_chrome_path(self):
        return self.chrome_path

    """
        for windows: https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_win32.zip
        for linux: https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_linux64.zip
    """

    def __download_chrome(self):
        current_os = methods.get_os()
        url = ""
        executable_chrome = ""
        if current_os == "nt":
            url = "https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_win32.zip"
            executable_chrome = "chromedriver.exe"
        elif current_os == "posix":
            url = "https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_linux64.zip"
            executable_chrome = "chromedriver"

        r = requests.get(url)
        temp_path = self.base_path + "temp"
        f = open(temp_path, mode="wb")
        f.write(r.content)
        f.close()

        zip_chrome = zipfile.ZipFile(temp_path)
        zip_chrome.extract(executable_chrome, self.base_path)
        zip_chrome.close()

        os.remove(temp_path)

        r.close()
