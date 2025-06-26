import asyncio
import socket
from contextlib import closing

import websockets


def find_free_port(start_port=8000, end_port=9000):
    """Находит первый свободный порт в заданном диапазоне"""
    for port in range(start_port, end_port + 1):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(('', port))
                s.close()
                return port
            except OSError:  # Порт занят
                continue
    raise ValueError(f"No free ports in range {start_port}-{end_port}")


class ClientWebSockets:
    def __init__(self, port):
        self.free_port = port
    
    def send_message(self, message):
        asyncio.run(self.run_connect(message))
    
    async def run_connect(self, message):
        await self.asend_message(message)
    
    async def asend_message(self, message):
        async with websockets.connect(f"ws://127.0.0.1:{self.free_port}") as client:
            await client.send(message)
