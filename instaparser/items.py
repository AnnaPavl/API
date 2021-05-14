# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    photo = scrapy.Field()
    use = scrapy.Field()
    full_name = scrapy.Field()
    podpiska = scrapy.Field()
    podpischik = scrapy.Field()
    _id = scrapy.Field()

