# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    only_id = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    put_time = scrapy.Field()

class TopicItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    only_id = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    put_time = scrapy.Field()

class CodesItem(scrapy.Item):
    id = scrapy.Field()
    father_id = scrapy.Field()
    codeid = scrapy.Field()
    region_id = scrapy.Field()
    plate_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    blog_url = scrapy.Field()
    
class QuotesItem(scrapy.Item):
    id = scrapy.Field()
    datatime = scrapy.Field()
    code_id = scrapy.Field()
    gao = scrapy.Field()
    kai = scrapy.Field()
    di = scrapy.Field()
    shou = scrapy.Field()
    before = scrapy.Field()
    zd_money = scrapy.Field()
    zd_range = scrapy.Field()
