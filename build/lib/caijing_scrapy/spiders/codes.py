# -*- coding: utf-8 -*-
#########################################################
#     网易财经上市公司及股票代码,板块分类爬取
#     网易财经APP行业爬取,新股爬取
#     by wooght 2017-10
#########################################################
import scrapy
import re
import time
from caijing_scrapy.items import CodesItem,PlatesItem
import json
from model import T

from scrapy.http import Request

#新股爬取  网易财经APP分类获取新股
class NewCodeSpider(scrapy.Spider):
    name = 'newcodes'
    allowed_domains = '163.com'
    url_model = 'http://m.money.163.com/stock/service/plate.json?appversion=ios_3.3.3&count=500&page=0&plateid=hy0%s'
    company_url_model = 'http://quotes.money.163.com/app/stock/%s_summary.json'
    new_companys = []
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL':'WARNING'
    }
    def __init__(self,*args,**kwargs):
        super(NewCodeSpider,self).__init__(*args,**kwargs)
        self.plates = []
        self.companys = []
        self.regions = {}
        self.select_plates()
    def select_plates(self):
        s = T.select([T.listed_plate.c.plateid]).where(T.listed_plate.c.father_id!=0)
        r = T.conn.execute(s)
        for pid in r.fetchall():
            plateid = pid[0]
            if(len(str(plateid))<5):
                plateid = '0'+str(plateid)
            self.plates.append(plateid)
        s = T.select([T.listed_company.c.codeid])
        r = T.conn.execute(s)
        for code in r.fetchall():
            self.companys.append(str(code[0]))
        s = T.select([T.listed_region.c.id,T.listed_region.c.name])
        r = T.conn.execute(s)
        for region in r.fetchall():
            region_dict = {}
            self.regions[region[1]] = region[0]
    def start_requests(self):
        for url in self.plates:
            rurl = self.url_model%(url)
            print(rurl)
            R = scrapy.Request(rurl,callback=self.parse)
            yield R
    def parse(self,response):
        json_str = response.body.decode('utf8')
        json_obj = json.loads(json_str,encoding='utf8')
        for code in json_obj['list']:
            symbol = int(code['SYMBOL'])
            if(str(symbol) not in self.companys):
                newscode = {}
                newscode['codeid'] = symbol
                newscode['plate_id'] = json_obj['PLATEID'][2:]
                newscode['name'] = code['NAME']
                newscode['code'] = code['CODE']
                print(newscode)
                R = scrapy.Request(self.company_url_model%(newscode['code']),meta=newscode,callback=self.companysparse,dont_filter=True)
                yield R
    def companysparse(self,response):
        items = CodesItem()
        json_str = response.body.decode('utf8')
        json_obj = json.loads(json_str,encoding='utf8')
        if(response.meta['code'][0]=='1'):
            shsz = 'sz'
        else:
            shsz = 'sh'
        items['codeid'] = json_obj['SYMBOL']
        items['plate_id'] = response.meta['plate_id']
        items['shsz'] = shsz
        items['region_id'] = self.regions[json_obj['data'][0]['DI_YU']]
        items['name'] = response.meta['name']
        print(items)
        yield items

#股票代码抓取
class CodesSpider(scrapy.Spider):
    name = 'codes'
    allowed_domains = ['money.163.com']
    start_urls = ['http://quotes.money.163.com/old/#query=dy001000&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0']

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
           'caijing_scrapy.middlewares.Codesmiddlewares.WooghtDownloadMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
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

#板块分类抓取
class PlatesSpider(scrapy.Spider):
    name = 'plates'
    allowed_domains = ['money.163.com']
    start_urls = [
                  'http://quotes.money.163.com/old/#query=hy007001&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0'
                ]

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
           'caijing_scrapy.middlewares.Platesmiddlewares.WooghtDownloadMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL':'WARNING'
    }

    def parse(self, response):
        items = PlatesItem()
        allli = response.xpath('//ul[@qvpath]/li')
        print(response.body.decode('utf-8'),len(allli))
        for dalei in allli:
            li = dalei.xpath('ul/li')
            father_id = dalei.xpath('@qquery').extract_first()[12:]                  #获取属性的值,不用text()
            items['plateid'] = father_id
            items['name'] = dalei.xpath('a/@title').extract_first()
            items['father_id'] = 0
            yield items
            for xiaolei in li:
                 items['plateid'] = xiaolei.xpath('@qid').extract_first()[2:]
                 items['name'] = xiaolei.xpath('a/text()').extract_first()
                 items['father_id'] = father_id
                 yield items

#修改股票对应板块分类
class UpplatesSpider(scrapy.Spider):
    name = 'upplates'
    allowed_domains = ['money.163.com']
    start_urls = [
                  'http://quotes.money.163.com/old/#query=hy004001&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0'
                ]

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
           'caijing_scrapy.middlewares.Platesmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL':'WARNING'
    }
    def start_requests(self):
        s = T.select([T.listed_plate.c.plateid],).where(T.listed_plate.c.plateid>4000).where(T.listed_plate.c.father_id>0)
        r = T.conn.execute(s)
        metas = []
        for i in r.fetchall():
            metas.append(str(i[0]))
        print(metas)
        return [Request(self.start_urls[0],meta={'plates':metas},callback=self.parse)] #请求网页,并把cookie保存在meta中

    def parse(self, response):
        items = CodesItem()
        trs = response.xpath('//tr')
        for item in trs:
            items['codeid'] = item.xpath('td[3]/a/text()').extract_first().strip()
            items['plate_id'] = item.xpath('td[1]/text()').extract_first().strip()
            print(items)
            yield items
