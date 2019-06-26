# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class XueshuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    index = Field()
    title = Field()             # 标题
    abstract = Field()          # 摘要
    authors = Field()           # 作者
    quote_num = Field()         # 引用量
    date = Field()              # 时间
    key_words = Field()         # 关键词
    free_sources = Field()      # 免费资源地址
    paperid = Field()           # paper的id
