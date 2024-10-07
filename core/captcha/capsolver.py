
import asyncio
import httpx
from typing import Any, Tuple

class CapsolverSolver:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10)
        self.create_task_url = 'https://api.capsolver.com/createTask'
        self.get_task_result_url = 'https://api.capsolver.com/getTaskResult'

    async def solve_recaptcha(self) -> Tuple[str, bool]:
        try:
            captcha_data = {'clientKey': self.api_key, 'task': {'type': 'ReCaptchaV2EnterpriseTaskProxyLess', 'websiteURL': 'https://app.gradient.network/', 'websiteKey': '6Lfe5TAqAAAAAI3mJZFYU17Rzjh9DB5KDRReuqYV'}}
            resp = await self.client.post(self.create_task_url, json=captcha_data)
            if resp.status_code == 200:
                return await self.get_captcha_result(resp.json().get('taskId'))
        except httpx.RequestError as err:
            return (str(err), False)
        except Exception as err:
            return (str(err), False)
        else:
            return ('Failed to create captcha task', False)

    async def get_captcha_result(self, task_id: str) -> Tuple[Any, bool]:
        try:
            for _ in range(20):
                resp = await self.client.post(self.get_task_result_url, json={'clientKey': self.api_key, 'taskId': str(task_id)})
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get('status') == 'failed':
                        return (result.get('errorDescription'), False)
                    if result.get('status') == 'ready':
                        return (result['solution'].get('gRecaptchaResponse', ''), True)
        except httpx.RequestError as err:
            return (str(err), False)
        except Exception as err:
            return (str(err), False)
        else:
            await asyncio.sleep(5)
            return ('Max time for solving exhausted', False)