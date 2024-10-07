
import aiohttp
import json
import os
from loguru import logger
import inquirer

class ClientAuth:

    def __init__(self):
        self.username = None
        self.password = None
        self.credentials_file = 'credentials.json'
        self.api_url = 'https://gradient-auth-api.onrender.com'

    async def authenticate_user(self, username: str, password: str) -> tuple[bool, str]:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.api_url}/login', json={'username': username, 'password': password}, ssl=False) as response:
                if response.status == 200:
                    self.username = username
                    self.password = password
                    return (True, 'Login successful')
                else:
                    error_details = await response.json()
                    return (False, error_details.get('detail', 'Unknown error occurred'))

    async def deactivate_session(self):
        if self.username and self.password:
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.api_url}/logout', json={'username': self.username, 'password': self.password}, ssl=False) as response:
                    if response.status == 200:
                        logger.info('>> Successfully logged out')
                    else:
                        error_details = await response.json()
                        logger.error(f"Failed to logout: {error_details.get('detail', 'Unknown error')}")

    def save_credentials(self):
        credentials = {'username': self.username, 'password': self.password}
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
        except IOError:
            logger.warning('Could not save credentials')

    def load_credentials(self):
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
                    return (credentials.get('username'), credentials.get('password'))
            except IOError:
                logger.warning('Could not load credentials')
        return (None, None)

    async def login(self):
        saved_username, saved_password = self.load_credentials()
        if saved_username and saved_password:
            logger.info(f'Found saved credentials for user: {saved_username}')
            use_saved = inquirer.confirm('Do you want to use saved credentials?', default=True)
            if use_saved:
                success, message = await self.authenticate_user(saved_username, saved_password)
                if success:
                    self.username = saved_username
                    self.password = saved_password
                    logger.info(f'User {saved_username} successfully authenticated')
                    return True
                logger.error(f'Authentication failed: {message}')
                if message != 'Maximum number of sessions reached':
                    os.remove(self.credentials_file)
                else:
                    return False
        return await self.manual_login()

    async def manual_login(self) -> bool:
        questions = [inquirer.Text('username', message='Enter username'), inquirer.Password('password', message='Enter password')]
        answers = inquirer.prompt(questions)
        success, message = await self.authenticate_user(answers['username'], answers['password'])
        if success:
            self.save_credentials()
            logger.info(f"User {answers['username']} successfully authenticated")
            return True
        logger.error(f'Authentication failed: {message}')
        return False

    async def run(self) -> bool:
        if not await self.login():
            return False
        return True