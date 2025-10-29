import os
import shutil

modules = ["API", "ApiPlugins", "APIService", "Common", "PathControl", "ColorControl"]

os.chdir(os.getcwd())

for module in modules:
    os.system(f"uv run stubgen {module}")
    os.chdir(f"{module}-stubs")
    os.system("uv run --active setup.py bdist_wheel")
    stubs = os.listdir("./dist")[0]
    shutil.move(f"./dist/{stubs}", "../dist")
    os.chdir("..")
    