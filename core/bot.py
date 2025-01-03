
from loader import captcha_solver, config
from models import Account
from utils import *
from .websocket import WebSocketClient
from .api import NodePayAPI
from .exceptions.base import APIError

class Bot(NodePayAPI):
    def __init__(self, account: Account):
        super().__init__(account)

    async def get_recaptcha_token(self) -> str:
        for _ in range(3):
            logger.info(f'Account: {self.account_data.email} | Solving captcha...')
            result, status = await captcha_solver.solve_recaptcha()
            if status:
                logger.success(f'Account: {self.account_data.email} | Captcha solved')
                return result
            logger.error(f'Account: {self.account_data.email} | {result} | Retrying...')
            await asyncio.sleep(3)
        else:  # inserted
            raise APIError('Captcha solving failed after 3 attempts')

    async def process_registration(self) -> bool:
        try:
            if not await check_if_email_valid(self.account_data.imap_server, self.account_data.email, self.account_data.password):
                return False
            logger.info(f'Account: {self.account_data.email} | Registering...')
            tokens = await self.sign_up()
            await self.lookup_sign_up(tokens['idToken'])
            recaptcha_token = await self.get_recaptcha_token()
            self.session.headers['authorization'] = f"Bearer {tokens['idToken']}"
            response = await self.send_email_verification(recaptcha_token)
            if not response or response.get('code', 0)!= 200:
                logger.error(f'Account: {self.account_data.email} | Failed to send email verification: {response}')
                return False
            else:  
                logger.info(f'Account: {self.account_data.email} | Email verification sent')
                code = await check_email_for_code(self.account_data.imap_server, self.account_data.email, self.account_data.password)
                if code is None:
                    logger.error(f'Account: {self.account_data.email} | Failed to get email verification code')
                    return False
        except APIError as error:
            if error.error_message and error.error_message.strip() == 'EMAIL_EXISTS':
                logger.warning(f'Account: {self.account_data.email} | Email already registered')
                return True
            logger.error(f'Account: {self.account_data.email} | Failed to register (APIError): {(error.error_message if error.error_message else str(error))}')
        except Exception as error:
            logger.error(f'Account: {self.account_data.email} | Failed to register: {error}')
        return False
        else:  # inserted
            await self.verify_email(code)
            logger.success(f'Account: {self.account_data.email} | Email verified')
            tokens = await self.get_access_token(tokens['refreshToken'])
            self.session.headers['authorization'] = f"Bearer {tokens['access_token']}"
            await self.bind_invite_code(config.invite_code)
            logger.success(f'Account: {self.account_data.email} | Registered successfully')
            return True

    async def process_farming(self):
        try:
            await self.perform_farming_actions()
        except Exception as error:
            logger.error(f'Account: {self.account_data.email} | Unknown exception while farming: {error} | Stopped')

    async def close_session(self):
        try:
            await self.session.close()
        except Exception as error:
            logger.debug(f'Account: {self.account_data.email} | Failed to close session: {error}')

    async def run_websocket_client(self, node_credentials: dict):
        client = WebSocketClient(self.account_data)
        return await client.connect(client_id=node_credentials['clientid'], username=node_credentials['username'], password=node_credentials['password'])

    async def verify_node(self, client_id: str):
        pass
        try:
            pass  # postinserted
        logger.error(f'Account: {self.account_data.email} | Node banned, stopping...')
        return
        except Exception as error:
            logger.error(f'Account: {self.account_data.email} | Failed to verify node: {error}')
        await asyncio.sleep(1800)

    async def process_login(self) -> bool:
        try:
            self.session = self.setup_session()
            logger.info(f'Account: {self.account_data.email} | Logging in...')
            await self.sign_in()
            logger.info(f'Account: {self.account_data.email} | Successfully logged in')
            return True
        except APIError as error:
            logger.error(f'Account: {self.account_data.email} | {error}')
            return False

    async def process_get_user_info(self) -> dict:
        try:
            if not await self.process_login():
                return {}
            user_info = await self.user_info()
            logger.success(f'Account: {self.account_data.email} | User info fetched')
            return user_info
        except APIError as error:
            logger.error(f'Account: {self.account_data.email} | {error}')
            return {}

    async def perform_farming_actions(self):
        if not await self.process_login():
            return
        node_credentials = await self.register_node()
        logger.info(f"Account: {self.account_data.email} | Node registered with ID: {node_credentials['clientid']}")
        websocket_task = asyncio.create_task(self.run_websocket_client(node_credentials))
        await asyncio.sleep(30)
        verify_task = asyncio.create_task(self.verify_node(node_credentials['clientid']))
        while True:
            if websocket_task.done() or websocket_task.cancelled():
                if not verify_task.cancelled():
                    verify_task.cancel()
                if not websocket_task.cancelled():
                    websocket_task.cancel()
                logger.info(f'Account: {self.account_data.email} | Retry farming in 10m')
                await asyncio.sleep(600)
                self.session = self.setup_session()
                return await self.perform_farming_actions()
            else:  # inserted
                if verify_task.done() or verify_task.cancelled():
                    logger.info(f'Account: {self.account_data.email} | Stopped farming')
                    if not websocket_task.cancelled():
                        websocket_task.cancel()
                    if not verify_task.cancelled():
                        verify_task.cancel()
                    return None
                await asyncio.sleep(3)
