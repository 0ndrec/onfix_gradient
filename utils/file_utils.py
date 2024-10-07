
import os
import csv
from loguru import logger

def export_results(results: list, module: str) -> None:
    if not os.path.exists('./results'):
        os.makedirs('./results')
    if module == 'register':
        success_txt = open('./results/registration_success.txt', 'w')
        failed_txt = open('./results/registration_failed.txt', 'w')
        for email, account_password, status in results:
            if status:
                success_txt.write(f'{email}:{account_password}\n')
            else:
                failed_txt.write(f'{email}:{account_password}\n')
    logger.debug('Results exported to results folder')

def export_statistics(users_data: list[dict]):
    if not os.path.exists('./results'):
        os.makedirs('./results')
    unique_users = []
    for data in users_data:
        if data and data['id'] not in unique_users:
            unique_users.append(data)
    with open('./results/statistics.csv', 'w', newline='') as file:
        fieldnames = ['ID', 'Username', 'Email', 'Invite code', 'Total points', 'Referrals']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        logger.debug('Exporting statistics to CSV file...')
        for data in unique_users:
            if data:
                writer.writerow({'ID': data['id'], 'Username': data['name'], 'Email': data['email'], 'Invite code': data['code'], 'Total points': int(data['point']['total']) / 100000, 'Referrals': data['stats']['invitee']})
    logger.debug('Export completed successfully.')