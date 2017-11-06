# -*- coding: utf-8 -*-

#
#     第一财经-新闻
#     by wooght 2017-10
#
import scrapy
import re
import time
from caijing_scrapy.items import NewsItem
import caijing_scrapy.providers.wfunc as wfunc

import caijing_scrapy.Db as T

#以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

class NewsSpider(CrawlSpider):
    name = 'news'
    allowed_domains = ['www.yicai.com','xueqiu.com']
    download_delay = 2                                              #设置下载延时
    start_urls = [
                    # 'http://www.yicai.com/news/5365720.html',
                    # 'https://xueqiu.com/7859591518/95051267',
                    'https://xueqiu.com',
                    'http://www.yicai.com/data/',
                    'http://www.yicai.com/news/comment/',
                    'http://www.yicai.com/news/gushi/',
                    'http://www.yicai.com/data/',
                    'http://www.yicai.com/news/hongguan/',
                 ]

    rules = (
        #第一财经
        Rule(LinkExtractor(allow=('http\:\/\/www\.yicai\.com\/news\/\d+\.html',)),callback='parse_yicai',follow=True,process_links='link_screen'),
        #雪球
        Rule(LinkExtractor(allow=('\/\d+\/\d+',)),callback='parse_xueqiu',follow=True,process_links='link_screen'),
        Rule(LinkExtractor(allow=('\/\d+\/column',)),callback='parse',follow=True,process_links='link_screen'),
    )

    old_link = []


    def __init__(self,*args,**kwargs):
        #调用父类沟站函数
        super(NewsSpider,self).__init__(*args, **kwargs)

        #查询已经存在的地址
        s = T.select([T.news.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])
        print(self.old_link)

    #地址去重/过滤
    def link_screen(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        return new_links

    #第一财经
    def parse_yicai(self,response):
        items = NewsItem()
        items['title'] = response.xpath('//head/title/text()').extract()[0].strip()
        thetime = response.xpath('//div[@class="m-title f-pr"]/h2//span[2]/text()').extract()[0].strip()
        items['put_time'] = wfunc.time_num(thetime,"%Y-%m-%d %H:%M")
        items['url'] = response.url
        h_num = re.search(r'\/(\d+)\.html',items['url'],re.I).group(1)
        items['only_id'] = h_num
        items['body'] = response.xpath('//div[@class="m-text"]').extract()[0].strip().encode('utf-8')
        print(items['put_time'])
        yield items

    #雪球头条
    def parse_xueqiu(self,response):
        items = NewsItem()
        items['title'] = response.xpath('//title/text()').extract()[0].strip()
        thetime = response.xpath('//a[@class="time"]/@data-created_at').extract()[0].strip()
        # thetime = wfunc.search_time(thetime)
        items['put_time'] = thetime
        url_re = re.search(r'.*\/(\d+)\/(\d+)$',response.url,re.I)
        items['url'] = response.url
        items['only_id'] = url_re.group(1)+url_re.group(2)
        items['body'] = response.xpath('//div[@class="article__bd__detail"]').extract()[0].strip()
        yield items
