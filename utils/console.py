
import os
import sys
import urllib3
from art import tprint
from loguru import logger

def setup():
    urllib3.disable_warnings()
    logger.remove()
    logger.add(sys.stdout, colorize=True, format='<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | - <white>{message}</white>')
    logger.add('./logs/logs.log', rotation='1 day', retention='7 days')

def show_dev_info():
    os.system('cls')
    tprint('JamBit')
    print('\x1b[36mChannel: \x1b[34mhttps://t.me/JamBitPY\x1b[34m')
    print('\x1b[36mGitHub: \x1b[34mhttps://github.com/Jaammerr\x1b[34m')
    print()