import os
from PySide6.QtCore import QStandardPaths

# Получить стандартные пути для иконок
icon_paths = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppDataLocation)
# icon_paths = [os.path.join(path, "icons") for path in icon_paths]

print("Возможные пути к системным иконкам:")
for path in icon_paths:
    if os.path.exists(path):
        print(path)