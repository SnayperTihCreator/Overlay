from plugins.ManagerTask.tasks import *
import yaml
from attrs import define, field
from Service.PrintManager import PrintManager


@define
class Trig(BaseTrigger):
    name = field(default="10", type=str)
    
    def check(self, *args, **kwargs) -> bool:
        return True
    
    @classmethod
    def restore(cls, data):
        print(data)
        return cls(data["name"])
    
    def save(self):
        return {"name": self.name}
    
class Executor(BaseExecutor):
    
    def execute(self, *args, **kwargs) -> bool:
        print(args, kwargs)
        return True
    
    @classmethod
    def restore(cls, data):
        return cls()
    
    def save(self):
        return {}
    
    
act = Action(Executor(), Trig())

task = Task("exem", 1, [act])


with PrintManager() as pm:
    pm.show_caller_info(True)
    
    with open("output.yml", "w", encoding="utf-8") as file:
        yaml.dump(task, file, yaml.SafeDumper)
    
    with open("output.yml", encoding="utf-8") as file:
        print(yaml.load(file, yaml.SafeLoader))
