# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import regex
from datetime import datetime
from unidecode import unidecode
from scrapy.exporters import BaseItemExporter


class VnnewscrawlerPipeline(object):
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.exporter = BaseItemExporter()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(download_dir=crawler.settings.get("DOWNLOAD_DIR", "downloads"))

    def process_item(self, item, spider):
        subdir = os.path.join(
            self.download_dir,
            spider.name,
            regex.sub(
                r"[\s_-]+", "-", unidecode(item.get("category", "unknown"))
            ).lower(),
        )
        os.makedirs(subdir, exist_ok=True)

        filename = os.path.join(
            subdir, item.get("code", datetime.now().strftime("%Y%m%d%H%M%S%f"))
        )
        with open(filename, "w", encoding="UTF-8") as fp:
            json.dump(
                dict(self.exporter._get_serialized_fields(item)),
                fp,
                indent=4,
                ensure_ascii=False,
            )
        return item
