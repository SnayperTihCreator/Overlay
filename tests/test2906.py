from evdev import UInput, ecodes as e

cap = {
    e.EV_KEY: [e.KEY_PLAYPAUSE]
}

with UInput(None, "OverlayKeyboard") as ui:
    ui.write(e.EV_KEY, 164, 1)
    ui.write(e.EV_KEY, 164, 0)
    ui.syn()
