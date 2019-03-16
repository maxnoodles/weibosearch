# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import re

import pymongo

from weibosearch.items import WeibosearchItem

class WeibosearchPipeline(object):

    def parse_time(self, datetime):
        if re.match('\d+月\d+日', datetime):
            datetime = time.strftime('%Y{}').format('年') + datetime
        if re.match('今天(.*)', datetime):
            datetime = re.match('今天(.*)', datetime).group(1).strip()
            datetime = time.strftime('%Y{}%m{}%d{}').format('年','月','日') + ' ' + datetime
        if re.match('\d+分钟', datetime):
            minute =  re.match('(\d+)', datetime).group(1)
            datetime = time.strftime('%Y{}%m{}%d{}  %H{}:%M{}',
                                     time.localtime(time.time() - float(minute) * 60)).format('年', '月', '日', '时', '分')
        return datetime


    def process_item(self, item, spider):
        if isinstance(item, WeibosearchItem):
            if item.get('content'):
                item['content'] = item['content'].lstrip(':').strip()
            if item.get('date'):
                item['date'] = item['date'].strip()
                item['date'] = self.parse_time(item['date'])
        return item

class MongoPipeline():

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE')

        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.table_name].update({'id':item.get('id')}, {'$set':dict(item)}, True)
        return item
