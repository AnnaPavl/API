import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from pymongo import MongoClient
from pprint import pprint

from pymongo.errors import DuplicateKeyError

client = MongoClient('localhost', 27017)
db = client['job']
vacancies = db.vacancies

id = 0
text = input("Укажите профессию, должность или компанию:  ")

params = {'clusters': 'true',
          'enable_snippets': 'true',
          'salary': '',
          'st': 'searchVacancy',
          'text': text}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}

main_url = 'https://hh.ru'
response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
dom = bs(response.text, 'html.parser')

vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})
vacancies_hh = []
while True:
    for vacancy in vacancy_list:
        current_vacancy = {}
        vacancy_data = vacancy.find('a', {'class': 'bloko-link'})
        vacancy_salary = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"},
                                      {'class': ['bloko-section-header-3', 'bloko-section-header-3_lite']})
        vacancy_link = vacancy_data['href']
        vacancy_name = vacancy_data.getText()
        website = main_url
        current_vacancy['name'] = vacancy_name
        current_vacancy['link'] = vacancy_link
        current_vacancy['website'] = website
        current_vacancy['_id'] = id
        id+=1
        if vacancy_salary == None:
            current_vacancy['min_salary'] = None
            current_vacancy['max_salary'] = None
            current_vacancy['currency'] = None

        else:
            salary = vacancy_salary.getText().replace("\u202f", "").split(' ')
            if len(salary) == 3 and salary[0] == 'от':
                current_vacancy['min_salary'] = int(salary[1])
                current_vacancy['max_salary'] = None
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 3 and salary[0] == 'до':
                current_vacancy['max_salary'] = int(salary[1])
                current_vacancy['min_salary'] = None
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 4:
                current_vacancy['max_salary'] = int(salary[2])
                current_vacancy['min_salary'] = int(salary[0])
                current_vacancy['currency'] = salary[-1]
        try:
            vacancies.insert_one(current_vacancy)
        except DuplicateKeyError:
            continue
    next_page = dom.find('a', {'data-qa': "pager-next"}, {'class': 'bloko-button'})
    if next_page != None:
        next_link = next_page['href']
        response = requests.get(main_url + next_link, headers=headers)
        dom = bs(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})
        continue
    else:
        break

total_vacancies_hh = pd.DataFrame(vacancies_hh)
params = {'keywords': text,
          'noGeo': 1}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}

main_url = 'https://www.superjob.ru'
response = requests.get(main_url + '/vacancy/search', params=params, headers=headers)
dom = bs(response.text, 'html.parser')

vacancy_list = dom.find_all('div', {'class': 'jNMYr GPKTZ _1tH7S'})

while True:
    for vacancy in vacancy_list:
        current_vacancy = {}
        vacancy_data = vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'})
        children_div = vacancy_data.find('a')
        vacancy_salary = vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'})
        salary = vacancy_salary.getText().replace("\xa0", " ").split(' ')
        if len(salary) == 2:
            current_vacancy['min_salary'] = None
            current_vacancy['max_salary'] = None
            current_vacancy['currency'] = None

        else:
            if len(salary) == 4 and salary[0] == 'от':
                current_vacancy['min_salary'] = int(salary[1] + salary[2])
                current_vacancy['max_salary'] = None
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 4 and salary[0] == 'до':
                current_vacancy['max_salary'] = int(salary[1] + salary[2])
                current_vacancy['min_salary'] = None
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 6:
                current_vacancy['max_salary'] = int(salary[3] + salary[4])
                current_vacancy['min_salary'] = int(salary[0] + salary[1])
                current_vacancy['currency'] = salary[-1]
        vacancy_link = main_url + children_div['href']
        vacancy_name = children_div.getText()
        website = main_url
        current_vacancy['name'] = vacancy_name
        current_vacancy['link'] = vacancy_link
        current_vacancy['website'] = website
        current_vacancy['_id'] = id
        id+=1
        try:
            vacancies.insert_one(current_vacancy)
        except DuplicateKeyError:
            continue
    next_page = dom.find('a', {'rel': "next"},
                             {'class': 'icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe'})
    if next_page != None:
        next_link = next_page['href']
        response = requests.get(main_url + next_link, headers=headers)
        dom = bs(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'jNMYr GPKTZ _1tH7S'})
        continue
    else:
        break

money = int(input('Укажите желаемый уровень дохода:  '))

for vacancy in db.vacancies.find({ '$or': [{'min_salary': { '$gte': money}}, {'max_salary': { '$gte': money}}]} ):
    pprint(vacancy)

