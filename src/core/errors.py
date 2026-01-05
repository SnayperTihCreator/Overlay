from attrs import define


@define(auto_exc=True)
class OAddonsNotFound(Exception):
    oaddons_name: str
    
    def __str__(self):
        return f"Not found {self.oaddons_name}.oaddons in resource"


@define(auto_exc=True)
class OAddonsInit(Exception):
    oaddons_name: str
    what: Exception
    
    def __str__(self):
        return f"Can't init oaddons <{self.oaddons_name}> from {self.what}"


@define(auto_exc=True)
class PluginBuild(Exception):
    plugin_name: str
    
    def __str__(self):
        return f"Can't build plugin <{self.plugin_name}>"