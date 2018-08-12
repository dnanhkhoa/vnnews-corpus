# -*- coding: utf-8 -*-

import json
import regex
from bs4 import BeautifulSoup
from scrapy import Spider, Request
from scrapy.loader.processors import SelectJmes
from ..items import ArticleLoader


class BaomoicomSpider(Spider):
    name = "baomoicom"
    home_url = "https://baomoi.com"
    allowed_domains = ["baomoi.com"]
    disallowed_urls = ["baomoi.com/404"]

    linebreak_regex = regex.compile(r"(?:\r*[\n\v])+")
    article_code_regex = regex.compile(r"\/c\/(\d+)\.epi", flags=regex.IGNORECASE)

    def start_requests(self):
        yield Request(
            url=self.home_url,
            callback=self.follow_categories,
            meta={"skip-dupfilter": True},
        )

    def follow_categories(self, response):
        category_urls = response.css("li[class*=child] > a::attr(href)").extract()

        for category_url in category_urls:
            yield Request(
                url=response.urljoin(category_url),
                callback=self.follow_articles,
                meta={"skip-dupfilter": True},
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
                url=response.urljoin(next_page_url),
                callback=self.follow_articles,
                meta={"skip-dupfilter": True},
            )

    def parse_article(self, response):
        if all(map(lambda url: url not in response.url, self.disallowed_urls)):
            article_loader = ArticleLoader(response=response)
            article_loader.add_value(
                "code", self.article_code_regex.search(response.url).group(1)
            )
            article_loader.add_value("url", response.url)
            article_loader.add_css("category", "meta[property*=section]::attr(content)")

            article_info = json.loads(
                response.css("script[type='application/ld+json']::text").extract_first(
                    default="{}"
                )
            )
            article_loader.add_value("source", article_info, SelectJmes("author.name"))
            article_loader.add_value("headline", article_info, SelectJmes("headline"))
            article_loader.add_value(
                "description", article_info, SelectJmes("description")
            )
            article_loader.add_value("time", article_info, SelectJmes("dateModified"))

            article_soup = BeautifulSoup(
                response.css(".article__body").extract_first(), "lxml"
            )
            for br_tag in article_soup.find_all("br"):
                br_tag.replace_with("\n")

            lines = []
            for paragraph_tag in article_soup.find_all("p", class_="body-text"):
                for line in self.linebreak_regex.split(paragraph_tag.get_text()):
                    lines.append(line.strip())
            article_loader.add_value("content", "\n".join(lines))
            yield article_loader.load_item()
