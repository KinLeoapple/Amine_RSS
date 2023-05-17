# bs4 import
from bs4 import BeautifulSoup
# selenium import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# chrome
from core.web.init_chrome import InitChrome


class Condition:
    __slots__ = "condition"

    def __init__(self):
        self.condition = None
        self.condition: EC

    def by_title(self, title):
        self.condition = EC.title_is(title)
        return self.condition

    def by_alert(self):
        self.condition = EC.alert_is_present()
        return self.condition

    def by_css_presence(self, css_selector):
        self.condition = EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        return self.condition

    def by_css_presence_all(self, css_selector):
        self.condition = EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        return self.condition

    def by_css_clickable(self, css_selector):
        self.condition = EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        return self.condition

    def by_id_presence(self, html_id):
        self.condition = EC.presence_of_element_located((By.ID, html_id))
        return self.condition

    def by_id_presence_all(self, html_id):
        self.condition = EC.presence_of_all_elements_located((By.ID, html_id))
        return self.condition

    def by_id_clickable(self, html_id):
        self.condition = EC.element_to_be_clickable((By.ID, html_id))
        return self.condition

    def by_class_presence(self, class_name):
        self.condition = EC.presence_of_element_located((By.CLASS_NAME, class_name))
        return self.condition

    def by_class_presence_all(self, class_name):
        self.condition = EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        return self.condition

    def by_class_clickable(self, class_name):
        self.condition = EC.element_to_be_clickable((By.CLASS_NAME, class_name))
        return self.condition


class WaitConditionList:
    __slots__ = "conditions"

    def __init__(self):
        self.conditions: list = []

    def append(self, condition: Condition):
        self.conditions.append(condition)


class Spider:
    __slots__ = ("html", "driver")

    def __init__(self, url):
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        chrome_path = InitChrome().get_chrome_path()
        self.driver = webdriver.Chrome(executable_path=repr(chrome_path), options=option)
        self.driver.get(url)
        self.html = None

    def run(self, wait_conditions: WaitConditionList, timeout_sec=10):
        wait = WebDriverWait(self.driver, timeout_sec)

        for condition in wait_conditions.conditions:
            wait.until(condition)

        self.html = self.driver.page_source

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def get_html(self):
        return str(self.html) if self.html is not None else None


class HtmlSelector:
    __slots__ = "soup"

    def __init__(self, html):
        self.soup = BeautifulSoup(html, features="html.parser")

    def get_html(self):
        return self.soup.prettify()

    def select(self, selector):
        return self.soup.select(selector)
