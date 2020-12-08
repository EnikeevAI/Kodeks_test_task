import json

import requests

from Models import Vacancies
from config import celery_app, db


class WebPageInfoGetter:

    def __init__(self, request_params, web_page_for_search):
        self.web_page_for_search = web_page_for_search
        self.request_params = request_params

    def get_info_from_page(self):
        with requests.get(self.web_page_for_search, self.request_params) as req:
            info_on_page = req.content.decode()
        return json.loads(info_on_page)


class HHVacancyInfoGetter(WebPageInfoGetter):

    def __init__(self, page_number=0, number_of_vacancies_per_page=50):
        self.page_number = page_number
        self.number_of_vacancies_per_page = number_of_vacancies_per_page

    def set_request_params(self, vacancy_id=None, vacancy_name=None):
        if vacancy_id is not None:
            self.request_params = {}
            self.web_page_for_search = f'https://api.hh.ru/vacancies/{vacancy_id}'
        elif vacancy_name is not None:
            self.request_params = {
                'text': f'Name:{vacancy_name}',
                'page': self.page_number,
                'per_page': self.number_of_vacancies_per_page,
                'area': 2,
            }
            self.web_page_for_search = 'https://api.hh.ru/vacancies'



def create_vacancies_list(vacancy: str) -> list:
    vacancies_lst = []
    hh_info = HHVacancyInfoGetter()
    hh_info.set_request_params(vacancy_name=vacancy)
    number_of_vacancy_pages = hh_info.get_info_from_page()['pages']

    for page in range(number_of_vacancy_pages):
        hh_info.page_number = page
        vacancies_on_page = hh_info.get_info_from_page()['items']
        vacancies_lst = create_vacancies_list_task.delay(vacancies_on_page).get()
        add_vecancies_to_db.delay(vacancies_lst)
    return vacancies_lst


@celery_app.task
def create_vacancies_list_task(vacancies_on_page):
    vacancies_lst = []
    for vacancy in vacancies_on_page:
        web_page_for_search = f'https://api.hh.ru/vacancies/{vacancy["id"]}'
        with requests.get(web_page_for_search) as req:
            vacancy_description = json.loads(req.content.decode())
        vacancies_lst.append(vacancy_description)
    return vacancies_lst

@celery_app.task
def add_vecancies_to_db(vacancies_list):
    for vacancy in vacancies_list:
        db_vacancy = Vacancies(
            key_skills=", ".join([skill['name'] for skill in vacancy['key_skills']]),
            vacancy_name = vacancy['name'],
            salary_from = vacancy['salary']['from'] if vacancy['salary'] is not None else None,
            salary_to = vacancy['salary']['to'] if vacancy['salary'] is not None else None,
            description = vacancy['description'],
            vacancy_link = vacancy['alternate_url']
        )
        #db.session.add(db_vacancy)
        print(vacancy)


if __name__ == "__main__":
    task = create_vacancies_list('python junior')


