# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Article(Item):
    url = Field()
    source = Field()
    category = Field()
    title = Field()
    description = Field()
    content = Field()
    time = Field()
