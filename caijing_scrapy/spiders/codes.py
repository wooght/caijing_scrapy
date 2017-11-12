# -*- coding: utf-8 -*-
#
#     新浪网爬取上市公司及股票代码
#     by wooght 2017-10
#
import scrapy
import re
import time
from caijing_scrapy.items import NewsItem,TopicItem,CodesItem
import caijing_scrapy.providers.wfunc as wfunc

import caijing_scrapy.Db as T

#以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

class CodesSpider(scrapy.Spider):
    name = 'codes'
    allowed_domains = ['money.163.com']
    start_urls = ['http://quotes.money.163.com/old/#query=dy001000&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0']

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
           'caijing_scrapy.middlewares.Codesmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL':'WARNING'
    }


    def parse(self, response):
        items = CodesItem()
        trs = response.xpath('//tr')
        region_re = re.search(r'.*dy0(\d+)000',response.url,re.I)
        # items['region_id'] = int(region_re.group(1))
        for item in trs:
            items['name'] = item.xpath('td[4]/a[1]/text()').extract_first()
            if(items['name'] is None):
                items['name'] = item.xpath('td[4]/div/a/text()').extract_first().strip()
            items['codeid'] = item.xpath('td[3]/a/text()').extract_first().strip()
            items['region_id'] = item.xpath('td[1]/text()').extract_first().strip()
            print(items)
            yield items

    # # 地址生产
    # def __init__(self,*args,**kwargs):
    #     #调用父类沟站函数
    #     super(CodesSpider,self).__init__(*args, **kwargs)
    #
    #     print('__init__ is run......')
    #     str_url = "http://quotes.money.163.com/old/#query=dy0%s000&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0"
    #     start_urls = []
    #     s = T.select([T.listed_region.c.id])
    #     r = T.conn.execute(s)
    #     arr = r.fetchall()
    #     for i in arr:
    #         num = i[0]
    #         rs = str(num)
    #         if(num<10):
    #             rs = '0'+str(num)
    #         start_urls.append(str_url%(rs))
    #     print(start_urls)
    #     self.start_urls = start_urls
