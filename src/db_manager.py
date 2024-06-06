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
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v 
                JOIN companies c ON v.company_id = c.id
            """)
            return cur.fetchall()