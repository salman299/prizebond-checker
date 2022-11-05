"""
Python script to search prizebonds
"""

import os
import json
import logging
import argparse
from datetime import datetime
from utils import send_mails, generate_email_data, validate_user_credentials
from prize_bond_service import PrizeBondService, PrizeBondStatus

log = logging.getLogger(__name__)

def generate_report(prizebond_service, bonds_data):
    """
    Parse user data and returns prizebonds results
    Argumets:
        prizebond_service: (PrizeBondService)
        bonds_data: (dict)
    Returns:
        [
             {
                    "name": Ali,
                    "email": xyz@gmail.com,
                    "cc": [],
                    "draw": 100,
                    "date": 2022-01-16,
                    "body": '<p></p>',
            },
            {
                    "name": Kamran,
                    "email": abc@gmail.com,
                    "cc:: [],
                    "draw": 700,
                    "date": 2022-02-16,
                    "body": '<p></p>',
            }
        ]
    """
    final_result = []
    draws = prizebond_service.draws

    for draw, date in draws.items():
        for name, prizebonds in bonds_data.items():
            if draw in prizebonds['bonds'] and prizebonds['bonds'][draw]:
                log.info(f'Working for user:{name} draw:{draw}')
                person_data = {
                    "name": name,
                    "email": prizebonds.get('email'),
                    "draw": draw,
                    "date": date.split('/')[1],
                    "cc": prizebonds.get('cc', []),
                    "body": '',
                }
                items = prizebonds['bonds'][draw]
                start, end = list(zip(*items))
                start = [str(num) for num in start]
                end = [str(num) for num in end]
                results = prizebond_service.check_bonds(start, end, draw)
                if results['status'] == PrizeBondStatus.WON:
                    person_data['body'] = results['results']
                final_result.append(person_data)
    return final_result

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--month',
        type=int,
        choices=range(1, 12),
        default=datetime.now().month,
        help='Month of the year',
    )
    parser.add_argument(
        '-y',
        '--year',
        type=int,
        choices=range(2000, datetime.now().year),
        default=datetime.now().year,
        help='Year to search prizebond'
    )
    parser.add_argument(
        '-e',
        '--email',
        help="""
        Email used for sending email to other users
        you can also set EMAIL as env argument
        """
    )
    parser.add_argument(
        '-p',
        '--password',
        help="""
        Password of an email used to send emails to others
        You can also set PASSWORD as env argument
        """
    )
    parser.add_argument(
        '-f',
        '--file',
        default='sample.json',
        help= 'Path to the json file',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='print debug logs'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='print debug logs'
    )
    parser.add_argument(
        '-se',
        '--send-email',
        action='store_true',
        help='send email to users'
    )
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level = logging.DEBUG)
    elif args.info:
        logging.basicConfig(level = logging.INFO)
    if args.send_email:
        email = os.getenv('EMAIL', args.email)
        password = os.getenv('PASSWORD', args.password)
        if not (email and password):
            raise argparse.ArgumentTypeError('email and password are required')
        validate_user_credentials(email, password)
    
    year = int(os.getenv('YEAR', args.year))
    month = int(os.getenv('MONTH', args.month))
    log.info(f'Fetching data for year:{year} month:{month}')
    json_file = open(args.file)
    data = json.load(json_file)
    prizebond_service = PrizeBondService(year, month)
    log.info(f'Draws {prizebond_service.draws}')
    results = generate_report(prizebond_service, data)
    log.info(f'Results: {results}')
    if args.send_email:
        email_data = generate_email_data(email, results)
        log.info(email_data)
        send_mails(email, password, email_data)
