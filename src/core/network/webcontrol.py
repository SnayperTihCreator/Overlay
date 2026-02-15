import asyncio
import socket
from contextlib import closing
import logging
from threading import Thread

import websockets
from websockets.asyncio.server import serve
from websockets import exceptions as exc

logger = logging.getLogger(__name__)


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
    msg = f"No free ports available in range {start_port}-{end_port}"
    logger.critical(msg)
    raise ValueError(msg)


class ServerWebSockets(Thread):
    def __init__(self, ports, callback=None, nameServer=None):
        super().__init__(name=nameServer, daemon=True)
        self._callback = callback
        self.free_port = find_free_port(*ports)
        self._is_running = False
        self._event_loop = asyncio.get_event_loop_policy().new_event_loop()
        logger.info(f"Server initialized on port: {self.free_port}")
    
    def run(self):
        self._is_running = True
        logger.info("Server thread started.")
        try:
            self._event_loop.run_until_complete(self.runner())
        except Exception as e:
            logger.error(f"Server thread crashed: {e}", exc_info=True)
    
    def is_run(self):
        return self._is_running
    
    def quit(self):
        logger.info("Stopping server...")
        self._is_running = False
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)
    
    async def runner(self):
        logger.info(f"Serving on localhost:{self.free_port}")
        async with serve(self.handlerConnection, "localhost", self.free_port):
            while self._is_running:
                await asyncio.sleep(0.5)
    
    async def handlerConnection(self, wsock):
        try:
            async for msg in wsock:
                logger.debug(f"Message received: {msg}")
                if self._callback:
                    try:
                        self._event_loop.call_soon(self._callback, msg)
                    except Exception as e:
                        logger.error(f"Callback error processing message: {e}", exc_info=True)
        
        except exc.ConnectionClosed:
            logger.info("Client disconnected.")
        except Exception as e:
            logger.warning(f"Connection error: {e}")


class ClientWebSockets:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    
    def send_message(self, message):
        try:
            return asyncio.run(self.run_connect(message))
        except Exception as e:
            logger.error(f"Failed to run async loop for client: {e}", exc_info=True)
            return f"[red]System Error: {e}[/red]"
    
    async def run_connect(self, message):
        return await self.asend_message(message)
    
    async def asend_message(self, message):
        uri = f"ws://{self.ip}:{self.port}"
        logger.debug(f"Connecting to {uri}...")
        
        try:
            async with websockets.connect(
                    uri,
                    ping_interval=None,
                    extensions=None,
                    open_timeout=5,
                    additional_headers={
                        "User-Agent": "Python/3.11 websockets/15.0",
                        "Origin": "http://127.0.0.1"
                    }
            ) as client:
                
                logger.debug(f"Sending message: {message}")
                await client.send(message)
                
                try:
                    response = await asyncio.wait_for(client.recv(), timeout=10.0)
                    logger.debug(f"Response received: {response}")
                    return response
                except asyncio.TimeoutError:
                    logger.warning("Server timed out waiting for response.")
                    return "[red]Error: Server received command but timed out.[/red]"
        
        except ConnectionRefusedError:
            logger.warning(f"Connection refused to {uri}. Is server running?")
            return "[red]Error: Connection refused.[/red]"
        except Exception as e:
            logger.error(f"Client socket error: {e}", exc_info=True)
            return f"[red]Connection Error: {e}[/red]"
