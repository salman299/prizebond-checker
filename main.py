import requests
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from utils import send_mail

url = 'https://prizebond.result.pk/pb-ajax.php'

def get_draws(draw_value):
    draw_results = requests.post(url, data={'draw': draw_value})
    soup = BeautifulSoup(draw_results.text, "html.parser")
    dates = [option["value"] for option in soup.find_all("option")]
    return dates

def get_draws_of_current_month(draw_list=['200', '750', '1500'], months_back=0):
    current_draws = {}
    for draw in draw_list:
        draws = get_draws(draw)
        date_time_str = draws[1].split('/')[1]
        draw_date = datetime.strptime(date_time_str, '%Y-%m-%d')
        if datetime.now().month == draw_date.month + months_back:
            current_draws[draw] = draws[1]
    return current_draws

def generate_report(bonds_data ,check_last=1, draw_list=['200', '750', '1500']):
    draws = get_draws_of_current_month(draw_list)
    final_result = []

    for draw, date in draws.items():
        for name, prizebonds in bonds_data.items():
            if draw in prizebonds['bonds'] and prizebonds['bonds'][draw]:
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

if __name__ == "__main__":
    email = os.getenv('EMAIL')
    password = os.environ.get('PASSWORD')
    json_file = open('sample.json')
    data = json.load(json_file)
    results = generate_report(data)
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
