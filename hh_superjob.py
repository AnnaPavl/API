import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

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
        if vacancy_salary == None:
            current_vacancy['min_salary'] = 'Не указана'
            current_vacancy['max_salary'] = 'Не указана'
            current_vacancy['currency'] = 'Не указана'

        else:
            salary = vacancy_salary.getText().replace("\u202f", "").split(' ')
            if len(salary) == 3 and salary[0] == 'от':
                current_vacancy['min_salary'] = salary[1]
                current_vacancy['max_salary'] = 'Не указана'
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 3 and salary[0] == 'до':
                current_vacancy['max_salary'] = salary[1]
                current_vacancy['min_salary'] = 'Не указана'
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 4:
                current_vacancy['max_salary'] = salary[2]
                current_vacancy['min_salary'] = salary[0]
                current_vacancy['currency'] = salary[-1]
        vacancies_hh.append(current_vacancy)
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
vacancies_sj = []
while True:
    for vacancy in vacancy_list:
        current_vacancy = {}
        vacancy_data = vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'})
        children_div = vacancy_data.find('a')
        vacancy_salary = vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'})
        salary = vacancy_salary.getText().replace("\xa0", " ").split(' ')
        if len(salary) == 2:
            current_vacancy['min_salary'] = 'По договорённости'
            current_vacancy['max_salary'] = 'По договорённости'
            current_vacancy['currency'] = 'Не указана'

        else:
            if len(salary) == 4 and salary[0] == 'от':
                current_vacancy['min_salary'] = salary[1] + salary[2]
                current_vacancy['max_salary'] = 'Не указана'
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 4 and salary[0] == 'до':
                current_vacancy['max_salary'] = salary[1] + salary[2]
                current_vacancy['min_salary'] = 'Не указана'
                current_vacancy['currency'] = salary[-1]
            if len(salary) == 6:
                current_vacancy['max_salary'] = salary[3] + salary[4]
                current_vacancy['min_salary'] = salary[0] + salary[1]
                current_vacancy['currency'] = salary[-1]
        vacancy_link = main_url + children_div['href']
        vacancy_name = children_div.getText()
        website = main_url
        current_vacancy['name'] = vacancy_name
        current_vacancy['link'] = vacancy_link
        current_vacancy['website'] = website
        vacancies_sj.append(current_vacancy)
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
total_vacancies_sj = pd.DataFrame(vacancies_sj)
total = vacancies_hh + vacancies_sj
total_df = pd.DataFrame(total)
print(total_df)
print(len(total))