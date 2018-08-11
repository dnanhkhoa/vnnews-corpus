# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.contrib.loader import ItemLoader


class Article(Item):
    code = Field()
    url = Field()
    source = Field()
    category = Field()
    headline = Field()
    description = Field()
    content = Field()
    time = Field(serializer=str)


class ArticleLoader(ItemLoader):
    default_item_class = Article
