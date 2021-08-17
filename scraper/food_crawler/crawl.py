from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

# NOTE: from here -
# https://doc.scrapy.org/en/latest/topics/practices.html#running-multiple-spiders-in-the-same-process

# Run the spiders on different processes, sequentially
configure_logging()
runner = CrawlerRunner(get_project_settings())

# Something that has to do with Twisted
@defer.inlineCallbacks
def crawl():
    yield runner.crawl('sdh')
    yield runner.crawl('ndh')
    reactor.stop()

# Execute
crawl()
reactor.run()