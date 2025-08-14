from PathControl.storageControls import OpenManager, decoPlugin

@decoPlugin("ManagerTask")
class A:
    def getIcon(self):
        return self, open("pldata://tasks.yml")


with OpenManager() as om:
    print(A().getIcon())
