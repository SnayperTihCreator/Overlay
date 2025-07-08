import Service.globalContext
from APIService.storageControls import OpenManager
from Service.PrintManager import PrintManager

from fs import open_fs
from fs.opener import registry
import assets_rc

with PrintManager() as pm, OpenManager() as om:
    pm.show_caller_info(True)
    with open("qt://main/main.css") as file:
        print(file.read())
        