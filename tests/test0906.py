from plugins.ManagerTask.tasks import *
from Service.PrintManager import PrintManager

with PrintManager() as pm:
    pm.show_caller_info(True)
    
    RunCommandExecutor(None, "explorer").execute()
    
    while True:
        pass

