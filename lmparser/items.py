# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose


# def process_photo_links(photo_url):
# correct_url = photo_url.replace('/s/', '/b/').replace('/m/', '/b/')
# return correct_url

def correct_characteristics(characteristics):
    # тут корявое преобразование данных по характеристикам, просьба не вникать
    new = []
    for i in characteristics:
        u = i.replace('\n', '')
        while True:
            if u[0] == ' ' and len(u) > 1:
                u = u[1:]
            if u[-1] == ' ' and len(u) > 1:
                u = u[:-1]
            else:
                break
        new.append(u)
    total = []
    for i in new:
        if i != ' ':
            total.append(i)
    char = {}
    c = 0
    while c < len(total):
        char[total[c]] = total[c + 1]
        c += 2

    return char


class LmparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    characteristics = scrapy.Field(input_processor=Compose(correct_characteristics))
    link = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field(output_processor=Compose(lambda v: int(v[0].replace('/', '').split('-')[-1])))
    price = scrapy.Field(output_processor=Compose(lambda v: float(v[0].replace(' ', ''))))
