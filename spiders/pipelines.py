# -*- coding: utf-8 -*

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class XueshuPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    def __init__(self):
        self.mongo_url = "mongodb://localhost:27017"

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client['paper']

    def process_item(self,item,spider):
        collection_name = 'keyword_%s' % item['index']
        self.db[collection_name].insert(dict(item))
        return item

    def close_spider(self):
        self.client.close()