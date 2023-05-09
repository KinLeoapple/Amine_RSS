import os.path


class Files:
    __slots__ = ("path", "file_list")

    def __init__(self, path):
        self.file_list = None
        self.path = path

    def get_files(self):
        self.file_list: list = []
        if os.path.exists(self.path):
            if os.path.isfile(self.path):
                root = os.path.dirname(self.path)
                filename = os.path.basename(self.path)
                self.__append_file(root, filename)
            else:
                self.__walk_dir()
            return self.file_list
        else:
            return []

    def clean_torrent_files(self):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if filename.lower().endswith(".torrent"):
                    os.remove(os.path.join(root, filename))
    
    def __walk_dir(self):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                self.__append_file(root, filename)
        
    def __append_file(self, root, file_name):
        self.file_list.append({"root": os.path.join(root, "").replace("\\\\", "/").replace("\\", "/"),
                               "name": file_name})
