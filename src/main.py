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
    user_agent = {'User-Agent': 'HH-User-Agent'}
    params = {
        'employer_id': company_id,
        'per_page': 100
    }
    response = requests.get(url, headers=user_agent, params=params)
    return response.json()


def create_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                hh_id INT UNIQUE NOT NULL
            );

        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            salary_from INT,
            salary_to INT,
            url TEXT NOT NULL,
            company_id INT REFERENCES companies(id)
        );
    """)


def main():
    # Подключение к базе данных
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()

    # Создание таблиц
    create_tables(cur)

    # Обработка данных для каждой компании
    for company_id in COMPANIES:
        vacancies_data = get_vacancies_for_company(company_id)
        # Получение информации о компании
        company_info = requests.get(f'https://api.hh.ru/employers/{company_id}').json()
        company_name = company_info['name']
        # Вставка информации о компании
        cur.execute("""
            INSERT INTO companies (name, hh_id)
            VALUES (%s,%s)
            ON CONFLICT (hh_id) DO NOTHING;
        """, (company_name, company_id))
        # Получение ID компании в базе данных
        cur.execute("SELECT id FROM companies WHERE hh_id=%s;", (company_id,))
        company_db_id = cur.fetchone()[0]
        # Вставка данных о вакансиях
        for item in vacancies_data['items']:
            title = item['name']
            salary_from = item['salary']['from'] if item['salary'] else None
            salary_to = item['salary']['to'] if item['salary'] else None
            url = item['alternate_url']

            cur.execute("""
                INSERT INTO vacancies (title, salary_from, salary_to, url, company_id)
                VALUES(%s, %s, %s, %s, %s);
            """, (title, salary_from, salary_to, url, company_db_id))

    # Сохранение изменений в базе данных
    conn.commit()

    # Закрытие курсора и подключения
    cur.close()
    conn.close()
    # Работа с классом DBManager
    db_manager = DBManager(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST)

    print("Компании и количество вакансий:")
    print(db_manager.get_companies_and_vacancies_count())
    #
    print("\nВсе вакансии:")
    print(db_manager.get_all_vacancies())

    print("\nСредняя зарплата:")
    print(db_manager.get_avg_salary())

    print("\nВакансии с зарплатой выше средней:")
    print(db_manager.get_vacancies_with_higher_salary())

    print("\nВакансии с ключевым словом 'Python':")
    print(db_manager.get_vacancies_with_keyword('Python'))

    db_manager.close()

if __name__ == '__main__':
    main()