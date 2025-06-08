drg = ["updateData", "loadConfig", "reloadConfig", "shortcut_run", "toggle_input", "savesConfig", "restoreConfig", "highlightBorder", "createSettingWidget"]

widg = ["reloadConfig", "savesConfig", "restoreConfig", "loader", "createSettingWidget"]

drg = set(drg)
widg = set(widg)

print(drg^widg)
print(drg&widg)