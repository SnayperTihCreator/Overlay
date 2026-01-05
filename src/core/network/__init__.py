from .webcontrol import ClientWebSockets, ServerWebSockets
try:
    from .q_webcontrol import ServerWebSockets as QServerWebSockets
except ImportError:
    pass