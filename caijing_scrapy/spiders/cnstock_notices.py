# -*- coding: utf-8 -*-
#
# 中国证券网 公告快讯爬取 notices
# 中国证券网 公司聚焦爬取 news
# 中国证券网 公司独家分析 topic
# by wooght 2017-11
#
import scrapy
import re
import time
from caijing_scrapy.items import NoticesItem,NewsItem,TopicItem
import caijing_scrapy.providers.wfunc as wfunc
import numpy as np

import caijing_scrapy.Db as T

#以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

'''
#公告快讯spider
#公告类 notices
'''
class Cnstock_noticesSpider(CrawlSpider):
    name = 'cnstock_notices'
    allowed_domains = ['cnstock.com']
    start_urls = ['http://ggjd.cnstock.com/gglist/search/ggkx']
    rules = (
        # 公告详细页面 http://ggjd.cnstock.com/company/scp_ggjd/tjd_ggkx/201711/4153740.htm
        Rule(LinkExtractor(allow=(r'company\/scp_ggjd\/tjd_ggkx\/\d+/\d+\.htm$',)),callback='parse_notices',follow=False),
    )
    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'DOWNLOAD_DELAY' : 2
    }

    def start_requests(self):
        totle_news = np.arange(50)
        for i in totle_news:
            url = 'http://ggjd.cnstock.com/gglist/search/ggkx/'+str(i)
            print(url)
            yield scrapy.Request(url,callback=self.parse)

    def parse_notices(self, response):
        items = NoticesItem()
        items['datatime'] = response.xpath('//span[@class="timer"]/text()').extract_first().strip()[:10]
        items['title'] = response.xpath('//h1[@class="title"]/text()').extract_first().strip()
        meta = response.xpath('//meta[@name="keywords"]/@content').extract_first()
        company = meta.split(' ')
        if(len(company)>1):
            items['code_id'] = company[0]
        else:
            items['code_id'] = 0
        items['body'] = ''
        body = response.xpath('//div[@id="qmt_content_div"]//p/text()').extract()
        for str in body:
            items['body']+=str
        wfunc.e('notices:'+items['title'])
        yield items

'''
#公司聚焦爬取spider
#新闻类 news
'''
class Cnstock_newsSpider(CrawlSpider):
    name = 'cnstock_news'
    allowed_domains = ['cnstock.com']
    start_urls = ['http://company.cnstock.com/company/scp_gsxw/']
    rules = (
        # 新闻详细页面 http://company.cnstock.com/company/scp_gsxw/201711/4153277.htm
        Rule(LinkExtractor(allow=(r'cnstock\.com\/company\/scp_gsxw\/\d+/\d+.htm$',)),callback='parse_news',follow=False,process_links='link_screen'),
    )
    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'DOWNLOAD_DELAY' : 2
    }
    old_link = []

    def start_requests(self):
        totle_news = np.arange(100)
        for i in totle_news:
            url = 'http://company.cnstock.com/company/scp_gsxw/'+str(i)
            yield scrapy.Request(url,callback=self.parse)

    def __init__(self,*args,**kwargs):
        #调用父类沟站函数
        super(Cnstock_newsSpider,self).__init__(*args, **kwargs)

        #查询已经存在的地址
        s = T.select([T.news.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])

    #地址去重/过滤
    #must return dict
    def link_screen(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        print('news urls:',len(new_links),' -=-=-==-old urls:',len(links)-len(new_links))
        return new_links

    def parse_news(self, response):
        items = NewsItem()
        thetime = response.xpath('//span[@class="timer"]/text()').extract_first().strip()[:10]
        items['put_time'] = wfunc.time_num(thetime,"%Y-%m-%d")
        items['title'] = response.xpath('//h1[@class="title"]/text()').extract_first().strip()
        items['body'] = ''
        body = response.xpath('//div[@id="qmt_content_div"]//p/text()').extract()
        for str in body:
            items['body']+=str
        items['url'] = response.url
        url_re = re.search(r'.*\/company\/scp_gsxw\/(\d+)\/(\d+).htm$',items['url'],re.I)  #http://company.cnstock.com/company/scp_gsxw/201711/4153765.htm
        items['only_id'] = url_re.group(1)+url_re.group(2)
        wfunc.e('news:'+items['title'])
        yield items


'''
#证券网独家解读spider
#评论,话题类 topic
'''
class Cnstock_topicsSpider(CrawlSpider):
    name = 'cnstock_topics'
    allowed_domains = ['cnstock.com']
    start_urls = ['http://ggjd.cnstock.com/gglist/search/qmtbbdj/']
    rules = (
        # 证券网独家解读 topics
        Rule(LinkExtractor(allow=(r'scp_ggjd\/tjd_bbdj\/\d+\/\d+\.htm$')),callback='parse_topic',follow=False,process_links='link_screen_topic'),
    )
    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'DOWNLOAD_DELAY' : 2
    }
    old_link = []

    def start_requests(self):
        totle_news = np.arange(50)
        for i in totle_news:
            url = 'http://ggjd.cnstock.com/gglist/search/qmtbbdj/'+str(i)
            yield scrapy.Request(url,callback=self.parse)

    def __init__(self,*args,**kwargs):
        #调用父类沟站函数
        super(Cnstock_topicsSpider,self).__init__(*args, **kwargs)

        #查询已经存在的地址
        s = T.select([T.topic.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])

    #地址去重/过滤
    def link_screen_topic(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        print('news urls:',len(new_links),' -=-=-==-old urls:',len(links)-len(new_links))
        return new_links

    def parse_topic(self,response):
        items = TopicItem()
        thetime = response.xpath('//span[@class="timer"]/text()').extract_first().strip()[:10]
        items['put_time'] = wfunc.time_num(thetime,"%Y-%m-%d")
        items['title'] = response.xpath('//h1[@class="title"]/text()').extract_first().strip()
        items['body'] = ''
        body = response.xpath('//div[@id="qmt_content_div"]//p/text()').extract()
        for str in body:
            items['body']+=str
        items['url'] = response.url
        url_re = re.search(r'.*\/company\/scp_ggjd\/tjd_bbdj\/(\d+)\/(\d+).htm$',items['url'],re.I)  #http://ggjd.cnstock.com/company/scp_ggjd/tjd_bbdj/201604/3765369.htm
        items['only_id'] = url_re.group(1)+url_re.group(2)
        wfunc.e('topics:'+items['title'])
        yield items
