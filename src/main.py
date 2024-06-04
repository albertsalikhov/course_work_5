import requests
import psycopg2
from db_manager import DBManager

# Константы для подключения к базе данных
DB_NAME = 'hh.ru'
DB_USER = 'postgres'
DB_PASSWORD = '321'
DB_HOST = 'localhost'

# Список интересующих компаний (их ID на hh.ru)
COMPANIES = [
    39305,
    3529,
    3664,
    1740,
    3127,
    15478,
    84585,
    78638,
    2180
]


def get_vacancies_for_company(company_id):
    url = 'https://api.hh.ru/vacancies'
    user_agent = {'User-Agent': 'HH-User-agent'}
    params = {
        'employer_id': company_id,
        'per_page': 100
    }
    response = requests.get(url, headers=user_agent, params=params)
    return response.json()
