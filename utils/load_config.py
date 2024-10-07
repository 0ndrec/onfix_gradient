
import os
import sys
import yaml
from sys import exit
from itertools import cycle
from loguru import logger
from models import Config, Account
from better_proxy import Proxy
CONFIG_PATH = os.path.join(os.getcwd(), 'config')
CONFIG_DATA_PATH = os.path.join(CONFIG_PATH, 'data')
CONFIG_PARAMS = os.path.join(CONFIG_PATH, 'settings.yaml')
REQUIRED_DATA_FILES = ('accounts.txt', 'proxies.txt')
REQUIRED_PARAMS_FIELDS = ('threads', 'capsolver_api_key', 'delay_before_start', 'imap_settings', 'invite_code')

def process_exit():
    input('Press Enter to exit...')
    exit(1)
pass

def read_file(file_path: str, check_empty: bool=True, is_yaml: bool=False) -> list[str] | dict:
    if not os.path.exists(file_path):
        logger.error(f'File not found: {file_path}')
        exit(1)
    if check_empty and os.stat(file_path).st_size == 0:
        logger.error(f'File is empty: {file_path}')
        exit(1)
    if is_yaml:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.readlines()
    return [line.strip() for line in data]

def get_params() -> dict:
    data = read_file(CONFIG_PARAMS, is_yaml=True)
    for field in REQUIRED_PARAMS_FIELDS:
        if field not in data:
            logger.error(f"Field '{field}' is missing in config2 file")
            process_exit()
    return data

def get_proxies() -> list[Proxy]:
    try:
        proxies = read_file(os.path.join(CONFIG_DATA_PATH, 'proxies.txt'), check_empty=False)
        if proxies:
            return [Proxy.from_str(line) for line in proxies]
        return []
    except Exception as exc:
        logger.error(f'Failed to parse proxy: {exc}')
        process_exit()

def get_accounts_to_register():
    proxies = get_proxies()
    proxy_cycle = cycle(proxies) if proxies else None
    accounts = read_file(os.path.join(CONFIG_DATA_PATH, 'register.txt'), check_empty=False)
    for account in accounts:
        try:
            email, password = account.split(':')
            yield Account(email=email, password=password, proxy=next(proxy_cycle) if proxy_cycle else None)
        except ValueError:
            logger.error(f'Failed to parse account: {account}')
            exit(1)

def get_accounts_to_farm():
    proxies = get_proxies()
    proxy_cycle = cycle(proxies) if proxies else None
    accounts = read_file(os.path.join(CONFIG_DATA_PATH, 'farm.txt'), check_empty=False)
    for account in accounts:
        try:
            email, password = account.split(':')
            yield Account(email=email, password=password, proxy=next(proxy_cycle) if proxy_cycle else None)
        except ValueError:
            logger.error(f'Failed to parse account: {account}')
            process_exit()

def validate_domains(accounts: list[Account], domains: dict):
    for account in accounts:
        try:
            domain = account.email.split('@')[1]
            if domain not in domains:
                logger.error(f"Domain '{domain}' is not supported, please add it to the config2 file")
                process_exit()
            imap_server = domains[domain]
            account.imap_server = imap_server
        except IndexError:
            logger.error(f'Failed to parse account: {account.email}')
            process_exit()
    return accounts

def load_config() -> Config:
    try:
        reg_accounts = list(get_accounts_to_register())
        farm_accounts = list(get_accounts_to_farm())
        if not reg_accounts and (not farm_accounts):
            logger.error('No accounts found in data files')
            process_exit()
        config = Config(**get_params(), accounts_to_farm=farm_accounts, accounts_to_register=reg_accounts)
        if reg_accounts:
            accounts = validate_domains(reg_accounts, config.imap_settings)
            config.accounts_to_register = accounts
        return config
    except Exception as exc:
        logger.error(f'Failed to load config: {exc}')
        process_exit()