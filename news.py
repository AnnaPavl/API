from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client['news_total']
news = db.news
# Лента
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'}
main_url = 'https://lenta.ru'
response = requests.get(main_url)

dom = html.fromstring(response.text)
months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
items = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[contains(@class,'item')]")
for item in items:
    news_1 = {}
    name = item.xpath(".//a/text()")[0].replace("\xa0", " ")
    date = item.xpath(".//time/@title")[0].split(' ')
    time = item.xpath(".//time/text()")[0]
    date = date[2] + '-' + months[date[1]] + '-' + date[0] + ' ' + time
    link = item.xpath("./a/@href")
    source = link[0].split('/')
    id = source[-5] + source[-4] + source[-3] + '-' + source[-2]
    #на https://lenta.ru/ есть новости со сторонних ресурсов
    if source[0] == 'https':
        link = item.xpath("./a/@href")[0]
        source = source[0] + '//' + source[2]
    else:
        source = main_url
        link = main_url + link[0]

    news_1['source'] = source
    news_1['date'] = date
    news_1['name'] = name
    news_1['link'] = link
    news_1['_id'] = id

    news.update_one({'_id': news_1['_id']}, {'$set': news_1}, upsert=True)

# Яндекс

main_url = 'https://yandex.ru/news'
response = requests.get(main_url)

dom = html.fromstring(response.text)
# Выберем новости Москвы и области
items = dom.xpath("//div[@class='mg-grid__col mg-grid__col_xs_12 mg-grid__col_sm_9']/div[3]/div[1] | //div[@class='mg-grid__col mg-grid__col_xs_12 mg-grid__col_sm_9']/div[3]/div[2]//div[@class='mg-grid__col mg-grid__col_xs_6']")
for item in items:
    news_1 = {}
    name = item.xpath(".//a[@class='mg-card__link']//text()")[0].replace("\xa0", " ")
    time = item.xpath(".//span[@class='mg-card-source__time']//text()")[0]
    date_today = str(datetime.date.today())
    date = date_today + ' ' + time
    link = item.xpath(".//div[@class='mg-card__text']/a/@href")[0]
    id = str(link).split('=')[-1]
    source = item.xpath(".//a[@class='mg-card__source-link']//text()")[0]


    news_1['source'] = source
    news_1['date'] = date
    news_1['name'] = name
    news_1['link'] = link
    news_1['_id'] = id

    news.update_one({'_id': news_1['_id']}, {'$set': news_1}, upsert=True)

#Mail
main_url = 'https://news.mail.ru/'
response = requests.get(main_url)

dom = html.fromstring(response.text)
# Выберем новости Москвы и Московской области

url = dom.xpath("//div[@class='layout']/div[2]/div[2]//a[contains(@class,'link')]/@href")
for link_one in url:
    response_one = requests.get(link_one)
    dom_2 = html.fromstring(response_one.text)
    items = dom_2.xpath("//body")
    for item in items:
        news_1 = {}
        name = item.xpath(".//h1//text()")
        date_time = item.xpath(".//span[@class='note__text breadcrumbs__text js-ago']/@datetime")[0]
        date = str(date_time).split("T")
        time = date[1].split(':')
        date_total = date[0] + ' ' + time[0] + ':' + time[1]
        link = link_one
        id = link.split('/')[-2]
        source = item.xpath(".//a[@class='link color_gray breadcrumbs__link']//@href")


        news_1['source'] = source[0]
        news_1['date'] = date_total
        news_1['name'] = name[0]
        news_1['link'] = link
        news_1['_id'] = id

        news.update_one({'_id': news_1['_id']}, {'$set': news_1}, upsert=True)