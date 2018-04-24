# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field

class UserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    repository = Field()
    # pass

class RepItem(scrapy.Item):
    name = Field()
    addr = Field()
    commitNum = Field()
    limitDate = Field()
    cmmtNum2Date = Field()
    cmmtNumFDate = Field()
