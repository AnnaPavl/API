import scrapy
from scrapy.http import HtmlResponse
from lmparser.items import LmparserItem
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LmruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        goods_links = response.xpath("//a[@data-qa='product-name']")
        for link in goods_links:
            yield response.follow(link, callback=self.pasrse_goods)

    def pasrse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=LmparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_value('link', response.url)
        loader.add_value('_id', response.url)
        loader.add_xpath('characteristics', "//dl[@class='def-list']//text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        yield loader.load_item()
