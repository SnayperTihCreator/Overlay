from PathControl.storageControls import OpenManager
from Service.PrintManager import PrintManager

with PrintManager() as pm, OpenManager() as om:
    pm.show_caller_info(True)
    with open("qt://main/main.css") as file:
        print(file.read())
        