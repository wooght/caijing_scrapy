# -*- coding: utf-8 -*-
import scrapy
import sys,io
import json
from scrapy import Request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8') #改变标准输出的默认编码
import time

class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['183.57.48.75']
    # url_models =   'http://183.57.48.75/ifzqgtimg/appstock/news/yaowen/get?nkey=getQQNewsListItemsVerify&returnType=0,1,6,100,102&ids=20171211A0D3LA00,20171211A0FF5100,20171211A0FDWQ00,20171211A0EQE200,20171211A0ES5600,20171211A0EBYH00,20171211A0F8V800,20171211A0F0RE00,20171211A0EQZG00,20171211A02NRB00,STO2017121101969701,STO2017121101969602,STO2017121101972101,STO2017121101978101,20171210A0MDVL00,STO2017121101960502,20171211A0E32900,20171211A0E1RA00,20171211A0D6BB00,STO2017121101880001,&_columnId=stock_yaowen_v2_new&check=1&app=3G&_rndtime=1512987049&_appName=ios&_dev=iPhone8,2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3&_uin=10000&_wxuin=20000'
    # url_modelss = 'http://183.57.48.75/ifzqgtimg/appstock/news/yaowen/get?nkey=getQQNewsListItemsVerify&returnType=0,1,6,100,102&ids=20171211A0D3BU00,20171211A0CY1Y00,STO2017121101884101,STO2017121101893401,STO2017121101893301,STO201712110023040A,STO2017121100295005,STO2017121100147606,STO2017121101894101,STO2017121101893701,STO2017121101893601,STO2017121101876202,STO2017121101893801,STO2017121101894001,STO2017121101893901,STO2017121101889601,20171211A0CIIQ00,20171211A0CXQD00,20171211A0CXYR00,20171211A0CS4S00,&_columnId=stock_yaowen_v2_new&check=1&app=3G&_rndtime=1512987213&_appName=ios&_dev=iPhone8,2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3&_uin=10000&_wxuin=20000'
    start_urls = ['http://183.57.48.75/ifzqgtimg/appstock/news/yaowen/get?nkey=getQQNewsIndexAndItemsVerify&returnType=0,1,6,100,102&ids=&_columnId=stock_yaowen_v2_new&check=1&app=3G&_rndtime=1512981869&_appName=ios&_dev=iPhone8,2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3&_uin=10000&_wxuin=20000']
    url_models = 'http://183.57.48.75/ifzqgtimg/appstock/news/NewsOpenProxy/get?nkey=getQQNewsSimpleHtmlContentVerify&id=%s&chlid=news_news_istock&return=0,1,6,100,102&devid=b7f6945c2c01d5275408b475f9d3d77deccf4fce&appver=iphone5.8.1&_omgid=7f37d4eaf6195b4505da3fa034f73aacf580001011161c&_columnId=stock_yaowen_v2_new&_rndtime=1512996494&_appName=ios&_dev=iPhone8,2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3&_uin=10000&_wxuin=20000'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,               #用scrapy自带的下载器中间件
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        "ITEM_PIPELINES" : {
           'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
        'LOG_LEVEL':'WARNING',
        'DOWNLOAD_DELAY' : 0.6,                                  #同一网站延迟时间
        'RANDOMIZE_DOWNLOAD_DELAY' : True,                     #随机等待时间 在download-delay的基础上,
        'DEFAULT_REQUEST_HEADERS' : {
          'Accept': '*/*',
          'Accept-Encoding': 'gzip,deflate',
          'Accept-Language': 'zh-cn',
          'User-Agent' : 'QQStock/17082410 CFNetwork/811.5.4 Darwin/16.7.0',
          'Referer':'http://zixuanguapp.finance.qq.com',
          "Connection": "keep-alive",
        }
    }
    api_headers = {
          'Accept': '*/*',
          'Accept-Encoding': 'gzip,deflate',
          'Accept-Language': 'zh-cn',
          'User-Agent' : 'QQStock/17082410 CFNetwork/811.5.4 Darwin/16.7.0',
          'Referer':'http://zixuanguapp.finance.qq.com',
          "Connection": "keep-alive",
          "Host": "183.57.48.75",
          "Connection": "keep-alive",

    }

    def parse(self, response):
        response_json = self.get_json(response)
        ids = response_json['data']['ids'][:5]
        print(ids)
        for id in ids:
            if('STO' in id):
                continue
            url = self.url_models%(id)
            R = Request(url=url,callback=self.html_parse,headers=self.api_headers,dont_filter=True)
            yield R
    def html_parse(self,response):
        api = self.get_json(response)
        print(api['data']['content']['text'])
        print(api['data']['surl'])
        print(api['data']['id'])
        print(api['data']['title'])

    def get_json(self,str):
        response_str = str.body.decode('utf-8')
        response_json = json.loads(response_str,encoding='utf8')
        return response_json
