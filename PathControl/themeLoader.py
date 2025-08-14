from fs import open_fs

from .loader import Loader


class ThemeLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder = open_fs("resource://theme")
    
    def load(self):
        pass
    
    def list(self):
        return self.folder.listdir("")
