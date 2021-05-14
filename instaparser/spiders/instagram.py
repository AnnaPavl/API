# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    #атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = 'sidi_i_molchi'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:9:1620918289:AVdQAMGRN4pl0pRupXet6v1TntcDWuMrpPHccxALMg9aO+8WmvwKx4YhMPZ925HtB4Ps+QKET6JY8e461F8D3+MfYwJXIRsfAEwy253QzeJsd5I64bCwTcVEeYL6KhDT1YxhvnyWpbzKMd6gJGY/'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['romanromanovskiy88', 'elenaimarova']      #Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    podpischiki_hash = '5aefa9893005572d237da5068082d8d5'
    podpiski_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'#hash для получения данных по постах с главной страницы

    def parse(self, response:HtmlResponse):             #Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)   #csrf token забираем из html
        yield scrapy.FormRequest(                   #заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_pwd},
            headers={'X-CSRFToken':csrf_token}
        )

    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_user:#Проверяем ответ после авторизации
                yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{user}',
                    callback= self.user_data_parse,
                    cb_kwargs={'username':user}
            )


    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя
        variables={'id':user_id,                                    #Формируем словарь для передачи даных в запрос
                   'first':12}                                      #12 постов. Можно больше (макс. 50)
        url_podpiski = f'{self.graphql_url}query_hash={self.podpiski_hash}&{urlencode(variables)}'
        url_podpischiki = f'{self.graphql_url}query_hash={self.podpischiki_hash}&{urlencode(variables)}'#Формируем ссылку для получения данных о постах
        yield response.follow(
            url_podpiski,
            callback=self.user_podpiski_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )
        yield response.follow(
            url_podpischiki,
            callback=self.user_podpischiki_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )

    def user_podpiski_parse(self, response:HtmlResponse,username,user_id,variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.podpiski_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_podpiski_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        podpiski = j_data.get('data').get('user').get('edge_follow').get('edges')     #Сами посты
        for podpiska in podpiski:                                                                      #Перебираем посты, собираем данные
            item = InstaparserItem(
                podpiska = 'ok',
                podpischik='neok',
                user_id = user_id,
                photo = podpiska['node']['profile_pic_url'],
                full_name = podpiska['node']['full_name'],
                use = podpiska['node']['username'],
                _id=podpiska['node']['id']
            )
        yield item                  #В пайплайн


    def user_podpischiki_parse(self, response:HtmlResponse,username,user_id,variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.podpischiki_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_podpischiki_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        podpischiki = j_data.get('data').get('user').get('edge_followed_by').get('edges')     #Сами посты
        for podpischik in podpischiki:                                                                      #Перебираем посты, собираем данные
            item = InstaparserItem(
                podpischik = 'ok',
                podpiska='neok',
                user_id = user_id,
                photo = podpischik['node']['profile_pic_url'],
                full_name = podpischik['node']['full_name'],
                use = podpischik['node']['username'],
                _id=podpischik['node']['id']
            )
        yield item




    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')