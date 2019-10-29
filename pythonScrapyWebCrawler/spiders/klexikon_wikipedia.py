import scrapy
from scrapy.spiders import CrawlSpider, Rule
from pythonScrapyWebCrawler.items import ArticleItem
from pythonScrapyWebCrawler.utils import processor


class KlexikonWikipediaSpider(CrawlSpider):

    name = 'klexikon_wikipedia'
    allowed_domains = ['klexikon.zum.de', 'de.wikipedia.org']
    start_urls = [
        'https://klexikon.zum.de/wiki/Kategorie:Klexikon-Artikel'
    ]

    def parse(self, response):
        for links in response.xpath('//div[@id="mw-pages"]'):
            next_page = links.css('a::attr(href)').extract()[0]
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_next)
            break

        for links in response.xpath('//div[@class="mw-content-ltr"]//li'):
            next_page = links.css('a::attr(href)').extract()[0]
            if 'wiki' in next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse_klexikon_article)

    def parse_next(self, response):
        for links in response.xpath('//div[@id="mw-pages"]'):
            next_page = links.css('a::attr(href)').extract()[1]
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_next)
            break

        for links in response.xpath('//div[@class="mw-content-ltr"]//li'):
            next_page = links.css('a::attr(href)').extract()[0]
            if 'wiki' in next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse_klexikon_article)

    def parse_klexikon_article(self, response):
        if 'https://klexikon.zum.de/wiki/Datei' in str(response.url):
            return

        title = processor.extract_title(response)
        content = processor.extract_content(response, '//div[@class="mw-content-ltr"]/*')
        content = processor.preprocess_content(content)

        article_item = ArticleItem()
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['content'] = content
        article_item['datasource'] = 'klexikon'
        yield article_item

        wikipedia_link = str(response.url).replace('https://klexikon.zum.de/', 'https://de.wikipedia.org/')
        yield scrapy.Request(wikipedia_link, callback=self.parse_wikipedia_article)

    def parse_wikipedia_article(self, response):
        title = processor.extract_title(response)
        content = processor.extract_content(response, '//div[@class="mw-content-ltr"]/div[@class="mw-parser-output"]/*')
        content = processor.preprocess_content(content)

        article_item = ArticleItem()
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['content'] = content
        article_item['datasource'] = 'wikipedia'
        yield article_item
