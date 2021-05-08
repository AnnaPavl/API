from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lmparser.spiders.lmru import LmruSpider
from lmparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # query = input('Введите наименование товара')
    process.crawl(LmruSpider, query='люстры')

    process.start()
