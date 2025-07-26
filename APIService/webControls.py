import asyncio
import socket
from contextlib import closing
from threading import Thread

import websockets
from websockets.asyncio.server import serve
from websockets import exceptions as exc


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


class ServerWebSockets(Thread):
    def __init__(self, ports, callback=None, nameServer=None):
        super().__init__(name=nameServer, daemon=True)
        self._callback = callback
        self.free_port = find_free_port(*ports)
        self._is_running = False
        self._event_loop = asyncio.get_event_loop_policy().new_event_loop()
    
    def run(self):
        self._is_running = True
        self._event_loop.run_until_complete(self.runner())
    
    def is_run(self):
        return self._is_running
    
    def quit(self):
        self._is_running = False
        self._event_loop.close()
    
    async def runner(self):
        async with serve(self.handlerConnection, "localhost", self.free_port) as server:
            while self._is_running:
                await asyncio.sleep(0.1)
    
    async def handlerConnection(self, wsock: websockets.ServerConnection):
        try:
            async for msg in wsock:
                self._event_loop.call_soon(self._callback, msg)
        except exc.ConnectionClosed:
            print("Клиент завершил")


class ClientWebSockets:
    def __init__(self, port):
        self.free_port = port
    
    def send_message(self, message):
        return asyncio.run(self.run_connect(message))
    
    async def run_connect(self, message):
        return await self.asend_message(message)
    
    async def asend_message(self, message):
        async with websockets.connect(f"ws://127.0.0.1:{self.free_port}") as client:
            await client.send(message)
            return await client.recv()
