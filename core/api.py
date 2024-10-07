
import asyncio
import json
import httpx
from uuid import uuid4
from typing import Literal, Tuple, Any
from curl_cffi.requests import AsyncSession
from models import Account
from .exceptions.base import APIError

class NodePayAPI:
    API_URL = 'https://api.gradient.network/api'
    GLOBAL_KEY = 'AIzaSyCWz-svq_InWzV9WaE3ez4XqxCE0C34ddI'

    def __init__(self, account: Account):
        self.account_data = account
        self.browser_id = str(uuid4())
        self.session = self.setup_session()

    def setup_session(self) -> AsyncSession:
        session = AsyncSession(impersonate='chrome124', verify=False)
        session.timeout = 10
        session.headers = {'accept': 'application/json, text/plain, */*', 'accept-language': 'en-US,en;q=0.9,ru;q=0.8', 'content-type': 'application/json', 'origin': 'https://app.gradient.network', 'priority': 'u=1, i', 'referer': 'https://app.gradient.network/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        if self.account_data.proxy:
            session.proxies = {'http': self.account_data.proxy.as_url, 'https': self.account_data.proxy.as_url}
        return session

    async def clear_request(self, url: str):
        session = AsyncSession(impersonate='chrome124', verify=False, timeout=10)
        session.proxies = self.session.proxies
        response = await session.get(url)
        return response
 

    async def send_request(self, request_type: Literal['POST', 'GET', 'OPTIONS']='POST', method: str=None, json_data: dict=None, params: dict=None, url: str=None, headers: dict=None, cookies: dict=None, verify: bool=True, max_retries: int=3, retry_delay: float=1.0):

        def verify_response(response_data: dict | list) -> dict | list:
            if isinstance(response_data, dict) and response_data.get('error'):
                raise APIError(f'API returned an error: {response_data}', response_data)
            if 'code' in str(response_data) and isinstance(response_data, dict) and (int(response_data.get('code')) != 200):
                raise APIError(f'API returned an error: {response_data}', response_data)
            return response_data
        for attempt in range(max_retries):
            try:
                if request_type == 'POST':
                    if not url:
                        response = await self.session.post(f'{self.API_URL}{method}', json=json_data, params=params, headers=headers if headers else self.session.headers, cookies=cookies)
                    else:
                        response = await self.session.post(url, json=json_data, params=params, headers=headers if headers else self.session.headers, cookies=cookies)
                elif request_type == 'OPTIONS':
                    response = await self.session.options(url, headers=headers if headers else self.session.headers, cookies=cookies)
                elif not url:
                    response = await self.session.get(f'{self.API_URL}{method}', params=params, headers=headers if headers else self.session.headers, cookies=cookies)
                else:
                    response = await self.session.get(url, params=params, headers=headers if headers else self.session.headers, cookies=cookies)
                if verify:
                    pass
                else:
                    try:
                        return verify_response(response.json())
                    except json.JSONDecodeError:
                        return response.text
                return response.text
            except APIError:
                raise
            except Exception as error:
                if attempt == max_retries - 1:
                    raise APIError(f'Failed to send request after {max_retries} attempts: {error}')
                await asyncio.sleep(retry_delay)
        raise APIError(f'Failed to send request after {max_retries} attempts')

    async def user_info(self) -> dict[str, Any]:
        response = await self.send_request(method='/user/profile', json_data={})
        return response['data']

    async def bind_invite_code(self, invite_code: str) -> dict[str, Any]:
        json_data = {'code': invite_code}
        response = await self.send_request(method='/user/register', json_data=json_data)
        return response

    async def get_access_token(self, refresh_token: str) -> dict[str, Any]:
        headers = {'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,ru;q=0.8', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://app.gradient.network', 'priority': 'u=1, i', 'referer': 'https://app.gradient.network/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'x-client-data': 'CKu1yQEIh7bJAQiitskBCKmdygEIq4nLAQiSocsBCJ3+zAEIhaDNAQjArM4BCNa9zgEY69PNAQ==', 'x-client-version': 'Chrome/JsCore/10.13.0/FirebaseCore-web', 'x-firebase-gmpid': '1:236765003043:web:4300552603f2d14908a096'}
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(url='https://securetoken.googleapis.com/v1/token', params={'key': self.GLOBAL_KEY}, data=data)
            response = response.json()
        return response

    async def verify_email(self, code: str) -> dict[str, Any]:
        json_data = {'code': code}
        response = await self.send_request(method='/user/verify/email', json_data=json_data)
        return response

    async def send_email_verification(self, recaptcha_token: str) -> dict[str, Any]:
        json_data = {'code': recaptcha_token}
        response = await self.send_request(method='/user/send/verify/email', json_data=json_data)
        return response

    async def lookup_sign_up(self, id_token: str):
        headers = {'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,ru;q=0.8', 'content-type': 'application/json', 'origin': 'https://app.gradient.network', 'priority': 'u=1, i', 'user-agent': self.session.headers['user-agent'], 'x-client-data': 'CKu1yQEIh7bJAQiitskBCKmdygEIq4nLAQiSocsBCJ3+zAEIhaDNAQjArM4BCNa9zgEY69PNAQ==', 'x-client-version': 'Chrome/JsCore/10.13.0/FirebaseCore-web', 'x-firebase-gmpid': '1:236765003043:web:4300552603f2d14908a096'}
        json_data = {'idToken': id_token}
        response = await self.send_request(url='https://identitytoolkit.googleapis.com/v1/accounts:lookup', json_data=json_data, params={'key': self.GLOBAL_KEY}, headers=headers)
        return response

    async def sign_up(self):
        headers = {'accept': '*/*', 'accept-language': 'en-US,en;q=0.9,ru;q=0.8', 'content-type': 'application/json', 'origin': 'https://app.gradient.network', 'priority': 'u=1, i', 'user-agent': self.session.headers['user-agent'], 'x-client-data': 'CKu1yQEIh7bJAQiitskBCKmdygEIq4nLAQiSocsBCJ3+zAEIhaDNAQjArM4BCNa9zgEY69PNAQ==', 'x-client-version': 'Chrome/JsCore/10.13.0/FirebaseCore-web', 'x-firebase-gmpid': '1:236765003043:web:4300552603f2d14908a096'}
        json_data = {'returnSecureToken': True, 'email': self.account_data.email, 'password': self.account_data.password, 'clientType': 'CLIENT_TYPE_WEB'}
        response = await self.send_request(url='https://identitytoolkit.googleapis.com/v1/accounts:signUp', json_data=json_data, params={'key': self.GLOBAL_KEY}, headers=headers)
        return response

    async def nodes_list(self) -> list[dict[str, Any]]:
        json_data = {'page': 1, 'size': 12, 'field': 'active', 'direction': 0, 'active': '', 'banned': ''}
        response = await self.send_request(method='/sentrynode/list', json_data=json_data)
        return response['data']

    async def send_node_status(self):
        headers = {'accept': 'application/json, text/plain, */*', 'accept-language': 'en-US,en;q=0.9,ru;q=0.8', 'authorization': self.session.headers['authorization'], 'priority': 'u=1, i', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'user-agent': self.session.headers['user-agent']}
        return await self.send_request(request_type='GET', method='/status', headers=headers)

    async def get_node_info(self, node_id: str) -> dict[str, Any]:
        response = await self.send_request(request_type='GET', method=f'/sentrynode/get/{node_id}')
        return response['data']

    async def register_node(self) -> dict[str, Any]:
        headers = {'accept': 'application/json, text/plain, */*', 'accept-language': 'ar-DZ,ar;q=0.9,en-US;q=0.8,en;q=0.7', 'authorization': self.session.headers['authorization'], 'content-type': 'application/x-www-form-urlencoded', 'origin': 'chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo', 'priority': 'u=1, i', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'user-agent': self.session.headers['user-agent']}
        return await self.send_request(request_type='POST', method='/sentrynode/register', headers=headers)

    async def sign_in(self) -> dict[str, Any]:
        json_data = {'returnSecureToken': True, 'email': self.account_data.email, 'password': self.account_data.password, 'clientType': 'CLIENT_TYPE_WEB'}
        response = await self.send_request(url='https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword', json_data=json_data, params={'key': self.GLOBAL_KEY})
        if response.get('idToken'):
            self.session.headers['authorization'] = f"Bearer {response['idToken']}"
            return response
        raise APIError(f'Failed to sign in: {response}')