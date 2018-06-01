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
    code_id = scrapy.Field()
    cp_attitude = scrapy.Field()
    plate_id = scrapy.Field()
    plate_attitude = scrapy.Field()
    article_id = scrapy.Field()
    article_type = scrapy.Field()

class QandaItem(scrapy.Item):
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
    code_id = scrapy.Field()
    cp_attitude = scrapy.Field()
    plate_id = scrapy.Field()
    plate_attitude = scrapy.Field()
    article_id = scrapy.Field()
    article_type = scrapy.Field()

class CodesItem(scrapy.Item):
    id = scrapy.Field()
    father_id = scrapy.Field()
    codeid = scrapy.Field()
    region_id = scrapy.Field()
    plate_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    blog_url = scrapy.Field()
    shsz = scrapy.Field()

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

class quotes_itemItem(scrapy.Item):
    id = scrapy.Field()
    quotes = scrapy.Field()
    code_id = scrapy.Field()
    update_at = scrapy.Field()

class PlatesItem(scrapy.Item):
    id = scrapy.Field()
    plateid = scrapy.Field()
    father_id = scrapy.Field()
    name = scrapy.Field()

class NoticesItem(scrapy.Item):
    id = scrapy.Field()
    datatime = scrapy.Field()
    code_id = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()

class DdtjItem(scrapy.Item):
    id = scrapy.Field()
    code_id  = scrapy.Field()
    only_id = scrapy.Field()
    totalamt = scrapy.Field()
    totalamtpct = scrapy.Field()
    totalvol = scrapy.Field()
    totalvolpct = scrapy.Field()
    stockvol = scrapy.Field()
    stockamt = scrapy.Field()
    kuvolume = scrapy.Field()
    kdvolume = scrapy.Field()
    kuamount = scrapy.Field()
    kdamount = scrapy.Field()
    avgprice = scrapy.Field()
    opendate = scrapy.Field()
class ZhchangeItem(scrapy.Item):
    id = scrapy.Field()
    zh_symbol  = scrapy.Field()
    change_id = scrapy.Field()
    stock_name = scrapy.Field()
    code_id = scrapy.Field()
    prev_weight = scrapy.Field()
    target_weight = scrapy.Field()
    change_status = scrapy.Field()
    updated_at = scrapy.Field()

class ZuheItem(scrapy.Item):
    id = scrapy.Field()
    zh_symbol  = scrapy.Field()
    zh_id = scrapy.Field()
    owner_id = scrapy.Field()
    zh_name = scrapy.Field()
