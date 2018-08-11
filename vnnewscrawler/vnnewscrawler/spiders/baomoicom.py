# -*- coding: utf-8 -*-

import regex
from scrapy import Spider, Request
from ..items import ArticleLoader


class BaomoicomSpider(Spider):
    name = "baomoicom"
    home_url = "https://baomoi.com"
    allowed_domains = ["baomoi.com"]

    article_code_regex = regex.compile(r"\/c\/(\d+)\.epi", flags=regex.IGNORECASE)

    def start_requests(self):
        yield Request(url=self.home_url, callback=self.follow_categories)

    def follow_categories(self, response):
        category_urls = response.css("li[class*=child] > a::attr(href)").extract()

        for category_url in category_urls:
            yield Request(
                url=response.urljoin(category_url), callback=self.follow_articles
            )

    def follow_articles(self, response):
        article_urls = response.css(
            ".timeline > div[data-aid] > div > .cache::attr(href)"
        ).extract()

        for article_url in article_urls:
            yield Request(
                url=response.urljoin(article_url), callback=self.parse_article
            )

        next_page_url = response.css(
            ".control__next[style*=inline]::attr(href)"
        ).extract_first()

        if next_page_url:
            yield Request(
                url=response.urljoin(next_page_url), callback=self.follow_articles
            )

    def parse_article(self, response):
        article_loader = ArticleLoader(response=response)
        yield article_loader.load_item()
