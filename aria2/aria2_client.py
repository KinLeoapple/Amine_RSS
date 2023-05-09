# aria2
from aria2.init_aria2 import InitAria2


class Aria2Client:

    def __init__(self):
        self.init_aria2 = InitAria2()

    def get_client(self):
        return self.init_aria2.get_aria2()


client = Aria2Client().get_client().client
