from APIService.storageControls import OpenManager

with OpenManager(True) as om:
    with open("project://config.toml") as file:
        print(file)
    with open("plugin://ClockDateWidget/config.toml") as file:
        print(file)