# -*- coding: utf-8 -*-
import json
import regex
import dateutil.parser
from scrapy import Spider, Request
from ..items import Article


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
        article_url = response.url

        code_matcher = self.article_code_regex.search(article_url)
        code = code_matcher and code_matcher.group(1)

        category = response.css(
            "meta[property*=section]::attr(content)"
        ).extract_first()
        category = category and category.strip()

        content = "\n".join(
            ["".join(p.css("::text").extract()).strip() for p in response.css(".body-text")]
        )

        article_info = json.loads(
            response.css("script[type='application/ld+json']::text").extract_first(
                default="{}"
            )
        )

        source = article_info.get("author")
        source = source and source.get("name")
        source = source and source.strip()

        headline = article_info.get("headline")
        headline = headline and headline.strip()

        description = article_info.get("description")
        description = description and description.strip()

        time = article_info.get("dateModified")
        time = time and dateutil.parser.parse(time.strip()).replace(tzinfo=None)

        yield Article(
            code=code,
            url=article_url,
            source=source,
            category=category,
            headline=headline,
            description=description,
            content=content,
            time=time,
        )
