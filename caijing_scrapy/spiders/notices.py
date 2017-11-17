# -*- coding: utf-8 -*-
#
# 巨潮资讯 深市上市公司公告爬取
# by wooght 2017-11
#
import scrapy
import re
import time
from caijing_scrapy.items import NoticesItem
import caijing_scrapy.providers.wfunc as wfunc


class NoticesSpider(scrapy.Spider):
    name = 'notices'
    allowed_domains = ['www.cninfo.com']
    start_urls = ['http://www.cninfo.com.cn/cninfo-new/disclosure/szse']

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
           'caijing_scrapy.middlewares.Noticesmiddlewares.WooghtDownloadMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
    }

    def parse(self, response):
        items = NoticesItem()
        body = response.xpath('//ul[@id="ul_his_fulltext"]/li')
        print(len(body))
        for i in body:
            items['code_id'] = i.xpath('div[@class="t1"]/font/text()').extract_first()
            items['title'] = i.xpath('div[@class="t3"]/dd/span/a/text()').extract_first()
            items['datatime'] = i.xpath('div[@class="t3"]/dd/span[2]/text()').extract_first()
            print(items)
            yield items
