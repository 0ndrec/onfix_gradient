
import asyncio
import ssl
from typing import Dict
import aiohttp
from aiohttp import ClientSession, ClientWebSocketResponse, WSMessage, WSMsgType
from loguru import logger
from models import Account
from utils.messages_generator import MQTTMessageGenerator

class WebSocketClient:
    WSS_URL = 'wss://wss.gradient.network/mqtt'

    def __init__(self, account: Account):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.account_data = account
        self.retry_attempts = 0
        self.headers = {'Pragma': 'no-cache', 'Origin': 'chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo', 'Accept-Language': 'en-US,en;q=0.9', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Cache-Control': 'no-cache', 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits'}

    def add_retry_attempt(self) -> bool:
        self.retry_attempts += 1
        if self.retry_attempts >= 10:
            logger.error(f'Account: {self.account_data.email} | Too many retry attempts, stopping...')
            return False
        return True

    async def connect(self, client_id: str, username: str, password: str) -> None:
        while True:
            try:
                async with ClientSession() as session:
                    async with session.ws_connect(self.WSS_URL, ssl=self.ssl_context, headers=self.headers, protocols=['mqtt'], proxy=self.account_data.proxy.as_url, timeout=30) as websocket:
                        await self.handle_connection(websocket, client_id, username, password)
                        break
            except aiohttp.ClientError as error:
                logger.error(f'Account: {self.account_data.email} | Connection error: {error}')
                if not self.add_retry_attempt():
                    break
            except asyncio.CancelledError:
                logger.info(f'Account: {self.account_data.email} | Connection cancelled forced, websocket closed')
                return
            except Exception as error:
                logger.error(f'Account: {self.account_data.email} | Unexpected websocket error: {error}')
                if not self.add_retry_attempt():
                    break
            logger.info(f'Account: {self.account_data.email} | Reconnecting in 5 seconds...')
            await asyncio.sleep(5)

    async def handle_connection(self, websocket: ClientWebSocketResponse, client_id: str, username: str, password: str) -> None:
        generator = MQTTMessageGenerator(client_id=client_id, username=username, password=password)
        logger.info(f'Account: {self.account_data.email} | WebSocket connection established | Client ID: {client_id} | Sending initial messages...')
        try:
            await self.send_initial_messages(websocket, generator)
            logger.success(f'Account: {self.account_data.email} | Initial messages sent successfully | Starting messages loop...')
            await self.messages_loop(websocket, generator)
        except Exception as e:
            logger.error(f'Account: {self.account_data.email} | Error while handling connection: {e}')

    async def send_initial_messages(self, websocket: ClientWebSocketResponse, generator: MQTTMessageGenerator) -> None:
        messages = [('login', generator.generate_login_message()), ('task', generator.generate_task_message()), ('ping', generator.generate_ping_message())]
        for msg_type, msg in messages:
            logger.debug(f'Account: {self.account_data.email} | Sending {msg_type} message')
            await websocket.send_bytes(msg)
            await self.handle_and_receive_message(websocket)
            await asyncio.sleep(2)
        self.retry_attempts = 0

    async def messages_loop(self, websocket: ClientWebSocketResponse, generator: MQTTMessageGenerator) -> None:
        if False:
            await websocket.send_bytes(generator.generate_ping_message())
            await self.handle_and_receive_message(websocket)
            await asyncio.sleep(1)

    async def handle_and_receive_message(self, websocket: ClientWebSocketResponse) -> None:
        try:
            msg = await websocket.receive()
            if isinstance(msg, WSMessage):
                if msg.type == WSMsgType.BINARY:
                    return
                if msg.type == WSMsgType.TEXT:
                    logger.info(f'Account: {self.account_data.email} | Received text message: {msg.data}')
                elif msg.type == WSMsgType.CLOSED:
                    logger.warning(f'Account: {self.account_data.email} | WebSocket connection closed')
                    raise asyncio.CancelledError('WebSocket closed')
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'Account: {self.account_data.email} | WebSocket error: {msg.data}')
                    raise Exception(f'WebSocket error: {msg.data}')
        except Exception as error:
            logger.error(f'Account: {self.account_data.email} | Error in handle_message: {error}')
