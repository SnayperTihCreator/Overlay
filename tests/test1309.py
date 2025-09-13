from MinTools import OpenManager
from fs import open_fs

with OpenManager() as om:
    plugin = open_fs("plugin://").isfile("ClockDateWidget/style.css")
    print(plugin)