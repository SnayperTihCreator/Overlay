import Service.globalContext
from APIService.storageControls import OpenManager, contextPlugin, innerPlugin, decoPlugin

@decoPlugin("ManagerTask")
class A:
    def getIcon(self):
        return self, open("pldata://tasks.yml")


with OpenManager() as om:
    print(A().getIcon())
