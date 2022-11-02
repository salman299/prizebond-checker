import requests
import os
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from utils import send_mail

logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)

url = 'https://prizebond.result.pk/pb-ajax.php'

def convert_draws_to_dict(draws):
    dates_dict = {}
    for draw in draws:
        try:
            date_time_str = draw.split('/')[1]
            draw_date = datetime.strptime(date_time_str, '%Y-%m-%d')
            if draw_date.year in dates_dict:
                dates_dict[draw_date.year][draw_date.month] = draw
            else:
                dates_dict[draw_date.year] = {draw_date.month : draw}
        except:
            continue
    return dates_dict

def get_draws(draw_value):
    draw_results = requests.post(url, data={'draw': draw_value})
    soup = BeautifulSoup(draw_results.text, "html.parser")
    dates = [option["value"] for option in soup.find_all("option")]
    return dates

def get_draws_of_year_month(year, month, draw_list):
    current_draws = {}
    for draw in draw_list:
        draws = get_draws(draw)
        draws_dict = convert_draws_to_dict(draws)
        if year in draws_dict and month in draws_dict[year]:
            current_draws[draw] = draws_dict[year][month]
    return current_draws

def generate_report(bonds_data, year, month, draw_list=['100', '200', '750', '1500']):
    
    draws = get_draws_of_year_month(year, month, draw_list)
    log.info(f'Draws held on {month}-{year} {draws}')
    final_result = []

    for draw, date in draws.items():
        for name, prizebonds in bonds_data.items():
            if draw in prizebonds['bonds'] and prizebonds['bonds'][draw]:
                log.info(f'Working for user:{name} draw:{draw}')
                person_data = {
                    "name": name,
                    "email": prizebonds['email'],
                    "draw": draw,
                    "date": date.split('/')[1],
                    "body": '',
                }
                items = prizebonds['bonds'][draw]
                number1, number2 = list(zip(*items))
                number1 = [str(num) for num in number1]
                number2 = [str(num) for num in number2]
                pb_data = {
                    'number1': ', '.join(number1),
                    'number2': ', '.join(number2),
                    'pb_draw_detail': date,
                    'draw_name': draw,
                }
                resp = requests.post(url, data = pb_data)
                soup = BeautifulSoup(resp.text, "html.parser")
                if len(soup.find_all('tr')) >= 3:
                    person_data['body'] += f'<p>{date}</p>{resp.text}</br>'
                final_result.append(person_data)
    return final_result

def get_current_or_valid_date(year, month, day=1):
    try:
        date = datetime(year, month, day)
    except:
        date = datetime.now()
    return date

if __name__ == "__main__":
    email = os.getenv('EMAIL')
    password = os.environ.get('PASSWORD')
    month = int(os.environ.get('MONTH', 0))
    year = int(os.environ.get('YEAR', 0))
    date = get_current_or_valid_date(year, month)

    json_file = open('sample.json')
    data = json.load(json_file)
    results = generate_report(data, date.year, date.month)
    for result in results:
        send_mail(
            email,
            password,
            result['email'],
            result['name'],
            result['draw'],
            result['date'],
            result['body']
        )
