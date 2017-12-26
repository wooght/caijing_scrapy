# -*- coding: utf-8 -*-
#
# 雪球访谈抓取
# by wooght 2017-11
# JS 接口 https://xueqiu.com/interview/answer/list.json?


import scrapy
import json
import providers.wfunc as wfunc
import re
from caijing_scrapy.items import QandaItem

class XqTalksSpider(scrapy.Spider):
    name = 'xq_talks'
    allowed_domains = ['xueqiu.com']
    start_urls = ['https://xueqiu.com/talks/all']

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,           #处理普通静态页面
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL':'WARNING'
    }

    # 处理首页  获取token
    def start_requests(self):
        r = scrapy.Request(self.start_urls[0],callback=self.wstart_parse)
        r.meta['phantomjs'] = True
        wfunc.e(r)
        yield r

    #访问API https://xueqiu.com/interview/list/backword.json?page=1&_=1511373425459
    # 获取页面当前最大ID
    def wstart_parse(self,response):
        title_str = response.xpath('//title/text()').extract_first()
        self.url_time = title_str.split(',')[0]
        self.token = title_str.split(',')[1]
        max_url = response.xpath("//ul[@id='backwordList']/li[1]/a/@href").extract_first()
        max_num = int(re.search(r'.*\/item/(\d+)',max_url).group(1))
        min_num = max_num-100
        while(max_num>min_num):
            max_num-=1
            url = "https://xueqiu.com/interview/answer/list.json?interviewId=%s&page=1&access_token=%s&_=%s"%(str(max_num),self.token,self.url_time)
            request_new = scrapy.Request(url,callback=self.page_parse)
            request_new.meta['max_num'] = str(max_num)
            yield request_new

    #获取回答内容
    def page_parse(self,response):
        item = QandaItem()
        max_num = response.meta['max_num']
        json_str = response.body
        json_obj = json.loads(json_str.decode('utf-8'))
        for one in json_obj['statuses']:
            item['body'] = one['description']
            item['only_id'] = one['id']
            item['put_time'] = one['created_at']
            item['url'] = response.url
            wfunc.e(str(one['id'])+',success')
            yield item
        #如果有翻页
        if(json_obj['maxPage']>1):
            num = json_obj['maxPage']
            while(num>1):
                url = "https://xueqiu.com/interview/answer/list.json?interviewId=%s&page=%s&access_token=%s&_=%s"%(str(max_num),num,self.token,self.url_time)
                request_new = scrapy.Request(url,callback=self.page_parse)
                request_new.meta['max_num'] = str(max_num)
                yield request_new
                num-=1
