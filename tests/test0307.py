import Service.globalContext
import APIService.storageControls
from Service.PrintManager import PrintManager

from fs import open_fs
from fs.opener import registry

with PrintManager() as pm:
    pm.show_caller_info(True)
    with open_fs("plugin://icon.png") as vfs:
        info = vfs.getinfo("icon.png")
        print(vfs.listdir(""))
        # vfs.makedir("O.zip")
        vfs = vfs.opendir("ClockDateWidget").opendir("ClockDateWidget")
        print(vfs.listdir(""))
        
    with open_fs("pldata://") as vfs:
        print(vfs.listdir(""))
        vfs = vfs.opendir("managerTask").opendir("tests")
        print(vfs.wrap_name)
        print(vfs.listdir(""))