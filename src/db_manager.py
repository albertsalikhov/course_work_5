import psycopg2


class DBManager:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(dbname= dbname, user=user, password=password, host=host)

    def get_companies_and_vacancies_count(self):
        """Метод для получения списка компаний и количества вакансий"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(v.id)
                FROM companies c
                LEFT JOIN vacancies v ON c.id=v.company_id
                GROUP BY c.name;
            """)
            return cur.fetchall()


    def get_all_vacancies(self):
        """Получаем все вакансии"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v 
                JOIN companies c ON v.company_id = c.id
            """)
            return cur.fetchall()

    def get_avg_salary(self):
        """Вычисляем среднюю зарплату в базе данных"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from+salary_to)/2)
                FROM vacancies 
                WHERE salary_from IS NOT NULL and salary_to IS NOT NULL
            """)
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        """Получаем вакансии с зарплатой выше среднего"""
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.id
                WHERE (v.salary_from + v.salary_to)/2 > %s
            """, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Получаем вакансии по ключевому слову"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.id
                WHERE v.title LIKE %s;
            """, (f'%{keyword}%',))
            return cur.fetchall()

    def close(self):
        self.conn.close()

