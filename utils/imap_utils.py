
import re
from typing import Optional
import asyncio
from bs4 import BeautifulSoup
from loguru import logger
from imap_tools import MailBox, AND

async def check_if_email_valid(imap_server: str, email: str, password: str) -> bool:
    logger.info(f'Account: {email} | Checking if email is valid...')
    try:
        await asyncio.to_thread(lambda: MailBox(imap_server).login(email, password))
        return True
    except Exception as error:
        logger.error(f'Account: {email} | Email is invalid (IMAP): {error}')
        return False
pass
pass

async def check_email_for_code(imap_server: str, email: str, password: str, max_attempts: int=8, delay_seconds: int=5) -> Optional[str]:
    code_pattern = '<div class="pDiv">\\s*([A-Z0-9])\\s*</div>'
    logger.info(f'Account: {email} | Checking email for code...')
    try:

        async def search_in_mailbox():
            return await asyncio.to_thread(lambda: search_for_code_sync(MailBox(imap_server).login(email, password), code_pattern))
        for attempt in range(max_attempts):
            link = await search_in_mailbox()
            if link:
                logger.success(f'Account: {email} | Code found: {link}')
                return link
            if attempt < max_attempts - 1:
                logger.info(f'Account: {email} | Code not found. Waiting {delay_seconds} seconds before next attempt...')
                await asyncio.sleep(delay_seconds)
        else:
            logger.warning(f'Account: {email} | Code not found after {max_attempts} attempts, searching in spam folder...')
            spam_folders = ('SPAM', 'Spam', 'spam', 'Junk', 'junk')
            for spam_folder in spam_folders:

                async def search_in_spam():
                    return await asyncio.to_thread(lambda: search_for_code_in_spam_sync(MailBox(imap_server).login(email, password), code_pattern, spam_folder))
                link = await search_in_spam()
                if link:
                    return link
            else:
                logger.error(f'Account: {email} | Code not found in spam folder after multiple attempts')
    except Exception as error:
        logger.error(f'Account: {email} | Failed to check email for code: {error}')

def search_for_code_sync(mailbox: MailBox, code_pattern: str) -> Optional[str]:
    messages = mailbox.fetch(AND(from_='noreply@gradient.network'))
    for msg in messages:
        body = msg.text or msg.html
        if body:
            match = re.search(code_pattern, body)
            if match:
                soup = BeautifulSoup(body, 'html.parser')
                code_divs = soup.find_all('div', class_='pDiv')
                code = ''.join((div.text.strip() for div in code_divs if div.text.strip()))
                if len(code) == 6:
                    return code
    else:
        return None

def search_for_code_in_spam_sync(mailbox: MailBox, link_pattern: str, spam_folder: str) -> Optional[str]:
    if mailbox.folder.exists(spam_folder):
        mailbox.folder.set(spam_folder)
        return search_for_code_sync(mailbox, link_pattern)