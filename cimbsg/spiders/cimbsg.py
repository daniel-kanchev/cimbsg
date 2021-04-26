import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cimbsg.items import Article
import requests
import json


class cimbsgSpider(scrapy.Spider):
    name = 'cimbsg'
    start_urls = ['https://www.cimb.com.sg/en/personal/important-notices.html']

    def parse(self, response):
        json_response = json.loads(requests.get("https://www.cimb.com.sg/en/personal/important-notices/_jcr_content/root/responsivegrid/news_listing_copy_co.list").text)
        months = json_response
        for month in months:
            articles = month["news"]
            for article in articles:
                link = response.urljoin(article['path'])
                date = article["publishDate"]
                title = article["title"]
                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date, title=title))

    def parse_article(self, response, date, title):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        content = response.xpath('//div[contains(@class, "rich")]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
