import scrapy
from scrapy.spiders import CrawlSpider, Rule
from pythonScrapyWebCrawler.items import ArticleItem


class KlexikonSpider(CrawlSpider):
    name = 'klexikon'
    allowed_domains = ['klexikon.zum.de']
    start_urls = [
        'https://klexikon.zum.de/wiki/Kategorie:Klexikon-Artikel'
    ]

    custom_settings = {
        'DEPTH_LIMIT': 3
    }

    def parse(self, response):
        for links in response.xpath('//div[@id="mw-pages"]'):
            next_page = links.css('a::attr(href)').extract()[0]
            print ("NEXT PAGGE")
            print (next_page)
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
            break

        for links in response.xpath('//div[@class="mw-content-ltr"]//li'):
            next_page = links.css('a::attr(href)').extract()[0]
            if 'wiki' in next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse_article)

    def parse_article(self, response):
        title = ''
        content = []

        for response_title in response.css('.firstHeading'):
            title = response_title.css('span::text').get()

        for node in response.xpath('//div[@class="mw-content-ltr"]//p'):
            content = content + node.xpath('string()').extract()

        content = content[:-1]
        content = ' '.join(content)
        content = content.replace('\n', '')
        content = content.replace('  ', ' ')

        article_item = ArticleItem()
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['content'] = content
        yield article_item
