from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# NOTE: from here -
# https://doc.scrapy.org/en/latest/topics/practices.html#running-multiple-spiders-in-the-same-process

# Run the spiders in the same process. Ideally, this will save time and money
# on GCE or GCK.
process = CrawlerProcess(get_project_settings())

# Run spiders
process.crawl('sdh')
process.crawl('ndh')
process.start()