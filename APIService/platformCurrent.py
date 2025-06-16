import sys
import os
from functools import cache


@cache
def isWayland() -> bool:
    """Определяет, работает ли система под Wayland."""
    # Проверяем несколько переменных окружения, связанных с Wayland
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    xdg_session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    # Дополнительные проверки для надежности
    has_wayland_env = any(
        key.startswith(("WAYLAND", "XDG_SESSION")) and "wayland" in os.environ.get(key, "").lower()
        for key in os.environ
    )
    return (
            "wayland" in xdg_session_type
            or (wayland_display is not None and wayland_display != "")
            or has_wayland_env
    )


@cache
def isProton() -> bool:
    """Определяет, запущена ли программа под Proton (в Linux или Windows)."""
    # Проверяем переменные окружения, связанные с Proton и Steam
    proton_env = os.environ.get("SteamEnv", "")
    steam_compat_data = os.environ.get("STEAM_COMPAT_DATA_PATH")
    steam_runtime = os.environ.get("SteamLinuxRuntime")
    # Дополнительные признаки Proton
    is_steam_proton = any(
        "proton" in os.environ.get(key, "").lower()
        for key in ("SteamGameId", "SteamAppId")
    )
    return (
            "SteamLinuxRuntime" in proton_env
            or steam_compat_data is not None
            or steam_runtime is not None
            or is_steam_proton
    )


@cache
def getSystem() -> list[str]:
    """Возвращает кортеж с информацией о платформе и оконной системе.

    Возвращает:
        tuple[str, str]: (platform, windowSystem)
        - platform: 'linux', 'win32', 'darwin' и т.д.
        - windowSystem: 'wayland', 'x11', 'native', 'proton' или '' (если неизвестно)
    """
    platform = sys.platform.lower()
    windowSystem = ""
    
    if platform.startswith("linux"):
        windowSystem = "wayland" if isWayland() else "x11"
    elif platform == "win32":
        windowSystem = "proton" if isProton() else "native"
    
    return [platform, windowSystem]


# Пример использования
if __name__ == "__main__":
    platform, windowSystem = getSystem()
    print(f"Platform: {platform}, Window System: {windowSystem}")