import asyncio
from utils import load_config
from core.captcha import capsolver
config = load_config()
captcha_solver = capsolver.CapsolverSolver(api_key=config.capsolver_api_key)
semaphore = asyncio.Semaphore(config.threads)