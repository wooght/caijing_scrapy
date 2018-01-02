# -*- coding: utf-8 -*-
import scrapy
import sys, io
import json
from scrapy import Request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 改变标准输出的默认编码
import time

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class TestSpider(CrawlSpider):
    name = 'test'
    allowed_domains = ['ganji.com', '58.com']
    start_urls = [
        # 赶集网 二手车
        # 'http://cd.ganji.com/ershouche/32403618028096x.htm',
        # 58同城二手房 经纪人
        'http://cd.58.com/ershoufang/h1/?PGTID=0d300000-0000-09f5-1294-11244f0307c2&ClickID=9'
    ]
    request_nums = 0
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 用scrapy自带的下载器中间件
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': 543,
        },
        "ITEM_PIPELINES": {
            'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
        'LOG_LEVEL': 'WARNING',
        'DOWNLOAD_DELAY': 0.6,  # 同一网站延迟时间
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机等待时间 在download-delay的基础上,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-cn',
            'User-Agent': 'QQStock/17082410 CFNetwork/811.5.4 Darwin/16.7.0',
            "Connection": "keep-alive",
        }
    }

    rules = (
        # 58同城二手房地址请求页面 58.com/ershoufang/32577425291463x.shtml?from
        Rule(LinkExtractor(allow=('58\.com\/ershoufang\/\d+x\.shtml',)), follow=True, process_links='link_screen',
             process_request='fang_request'),
        # process_request 指定对请求进行处理函数
    )

    def link_screen(self, urls):
        new_urls = []
        for url in urls:
            new_urls.append(url)
            self.request_nums+=1
            if self.request_nums>5:
                break
        return new_urls

    def fang_request(self,request):
        return Request(request.url,callback=self.wb_fang,meta={'phantomjs':True})


    def wb_fang(self, response):
        who_phone = response.xpath('//p[@class="phone-num"]/text()').extract()
        who_name = response.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div/a/text()').extract()
        print(who_name,':',who_phone)


