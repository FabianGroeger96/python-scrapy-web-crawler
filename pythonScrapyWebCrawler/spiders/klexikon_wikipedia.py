import scrapy
import re
from scrapy.spiders import CrawlSpider, Rule
from pythonScrapyWebCrawler.items import ArticleItem


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
                break

    def parse_next(self, response):
        for links in response.xpath('//div[@id="mw-pages"]'):
            next_page = links.css('a::attr(href)').extract()[1]
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_next)
            break

        for links in response.xpath('//div[@class="mw-content-ltr"]//li'):
            next_page = links.css('a::attr(href)').extract()[0]
            if 'wiki' in next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse_klexikon_article)
                break

    def parse_klexikon_article(self, response):
        if 'https://klexikon.zum.de/wiki/Datei' in str(response.url):
            return

        for response_title in response.css('.firstHeading'):
            title = response_title.css('span::text').get()

        content = ''
        for node in response.xpath('//div[@class="mw-content-ltr"]/*'):
            if '<p>' in node.get()[:5]:
                content = content + node.xpath('string()').extract()[0]

        content = self.preprocess_content(content)

        article_item = ArticleItem()
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['content'] = content
        article_item['datasource'] = 'klexikon'
        yield article_item

        wikipedia_link = str(response.url).replace('https://klexikon.zum.de/', 'https://de.wikipedia.org/')
        yield scrapy.Request(wikipedia_link, callback=self.parse_wikipedia_article)

    def parse_wikipedia_article(self, response):
        for response_title in response.xpath('//h1[@class="firstHeading"]'):
            title = response_title.xpath('string()').extract()[0]

        content = ''
        for node in response.xpath('//div[@class="mw-content-ltr"]/div[@class="mw-parser-output"]/*'):
            if '<p>' in node.get()[:5]:
                content = content + node.xpath('string()').extract()[0]

        content = self.preprocess_content(content)

        article_item = ArticleItem()
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['content'] = content
        article_item['datasource'] = 'wikipedia'
        yield article_item

    def preprocess_content(self, content):
        # remove line breaks
        content = re.sub(r'\n', '', content)
        # remove all brackets
        content = re.sub(r'\(.*?\)', '', content)
        content = re.sub(r'\{.*?\}', '', content)
        content = re.sub(r"\[.*?\]", '', content)
        content = re.sub(r'\<.*?\>', '', content)
        # replace "
        content = re.sub(r'(\“)+|(\„)+|(\")', "'", content)
        # replace . after number (19. Oct -> 19 Oct)
        for match in re.finditer(r'\d+?\.', content):
            content = content.replace(match.group(), match.group().replace('.', ''))
        # remove all * (lists)
        content = re.sub(r'(\*+)', '', content)
        # remove multiple whitespaces
        content = re.sub(r'\s+', ' ', content)
        # remove whitespaces before and after string
        content = content.strip()
        return content
