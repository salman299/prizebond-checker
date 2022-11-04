"""
Prizebond Services
"""

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from enum import Enum

class PrizeBondStatus(Enum):
    """
    Prizebond status codes
    """
    WON = 1
    LOSE = 0
    NOT_FOUND = -1

class PrizeBondService:
    """
    Service used to search prizebonds
    """
    url = 'https://prizebond.result.pk/pb-ajax.php'
    
    def __init__(self, year, month, draw_values=['100', '200', '750', '1500']):
        self.year = year
        self.month = month
        self.draw_values = draw_values
        self.draws = self.get_draws(year, month, draw_values)

    def _convert_draws_to_dict(self, draw_dates):
        """
        Parse list of draws to dict based on year and month
        Arguments:
            draw_dates: list(str) i.e ['01/2022-08-01', '03/2022-09-15', '03/2021-08-13']
        Returns:
            parsed values i.es
            {
                2022: {
                    8: '01/2022-08-01',
                    9: '03/2022-09-15',
                },
                2021: {
                    8: '03/2021-08-13'
                }
            }
        """
        dates_dict = {}
        for draw_str in draw_dates:
            try:
                date_time_str = draw_str.split('/')[1]
                draw_date = datetime.strptime(date_time_str, '%Y-%m-%d')
                if draw_date.year in dates_dict:
                    dates_dict[draw_date.year][draw_date.month] = draw_str
                else:
                    dates_dict[draw_date.year] = {draw_date.month : draw_str}
            except:
                continue
        return dates_dict

    def _get_draw_dates(self, draw_value):
            """
            Call an API and returns all draws
            Arguments:
                draw_value: (str) i.e 100, 200, 750, 1500
            Returns:
                list of draws i.e ['01/2022-08-01', '03/2022-09-15', '03/2021-08-13']
            """
            draw_results = requests.post(self.url, data={'draw': draw_value})
            soup = BeautifulSoup(draw_results.text, "html.parser")
            dates = [option["value"] for option in soup.find_all("option")]
            return dates

    def get_draws(self, year, month, draw_values):
            """
            Search all draws held in a month of a year
            Arguments:
                year: (int) i.e 2021, 2022
                month: (int) values from 1-12
                draw_values: list(str) draws to search in ['200', '750']
            Returns:
                {
                    '750': '03/2022-09-15',
                    '200': '03/2022-09-01''
                }
            """
            current_draws = {}
            for draw in draw_values:
                draws = self._get_draw_dates(draw)
                draws_dict = self._convert_draws_to_dict(draws)
                if year in draws_dict and month in draws_dict[year]:
                    current_draws[draw] = draws_dict[year][month]
            return current_draws

    def _parse_prizebond_response(self, response):
        """
        Parse response
        """
        soup = BeautifulSoup(response.text, "html.parser")
        if len(soup.find_all('tr')) >= 3:
            return {"status": PrizeBondStatus.WON, "results": response.text}
        return {"status": PrizeBondStatus.LOSE, "results": response.text}

    def check_bonds(self, start, end, draw_name):
        """
        Check prizebond
        """
        if draw_name in self.draws:
            pb_data = {
                'number1': ', '.join(start),
                'number2': ', '.join(end),
                'pb_draw_detail': self.draws[draw_name],
                'draw_name': draw_name,
            }
            response = requests.post(self.url, data = pb_data)
            return self._parse_prizebond_response(response)
        return {'status': PrizeBondStatus.NOT_FOUND, "results": None}
