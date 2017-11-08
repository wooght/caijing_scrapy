# -*- coding: utf-8 -*-

#
#     第一财经-新闻,腾讯证券,新闻股票,雪球头条
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
    allowed_domains = ['www.yicai.com','xueqiu.com','sina.com.cn','qq.com']
    download_delay = 1                                              #设置下载延时
    start_urls = [
                    # 'http://www.yicai.com/news/5365720.html',
                    # 'https://xueqiu.com/7859591518/95051267',
                    # 'http://finance.sina.com.cn/stock/s/2017-11-06/doc-ifynmvuq9022743.shtml'

                    'http://stock.qq.com/l/stock/ywq/list20150423143546.htm',
                    'http://finance.sina.com.cn/stock/',
                    'https://xueqiu.com',
                    'http://www.yicai.com/data/',
                    'http://www.yicai.com/news/comment/',
                    'http://www.yicai.com/news/gushi/',
                    'http://www.yicai.com/data/',
                    'http://www.yicai.com/news/hongguan/',

                 ]

    rules = (
        #新浪股票新闻
        Rule(LinkExtractor(allow=(r'\D*\/\d*\-\d*\-\d*\/doc\-\D*\d*\.shtml$',)),callback='parse_sina',follow=True,process_links='link_screen'),
        #第一财经
        Rule(LinkExtractor(allow=('http\:\/\/www\.yicai\.com\/news\/\d+\.html',)),callback='parse_yicai',follow=True,process_links='link_screen'),
        #雪球头条文章
        Rule(LinkExtractor(allow=('\/\d+\/\d+',),deny=('.*\.sina.*','.*\.htm',',*\.qq.*')),callback='parse_xueqiu',follow=True,process_links='link_screen'),
        Rule(LinkExtractor(allow=('\/\d+\/column',)),callback='parse',follow=True,process_links='link_screen'),
        #腾讯证券
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/a\/\d+\/\d+\.htm',)),callback='parse_qq_ywq',follow=False,process_links='link_screen'),
        # http://stock.qq.com/l/stock/ywq/list20150423143546_2.htm
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/.*\/list\d+\_\d+.htm',)),callback='parse',follow=True,process_links='link_screen'),
    )
        # LinkExtractor(allow=('\/\d+\/\d+',),deny=('.*\.sina.*','.*\.htm',',*\.qq.*'),restrict_xpaths=('//div[@id="id"]/a')) LinkExtractor通过xpaths指定搜索范围

    old_link = []

    #动态修改配置内容
    custom_settings = {
        'LOGSTATS_INTERVAL': 10,
    }


    def __init__(self,*args,**kwargs):
        #调用父类沟站函数
        super(NewsSpider,self).__init__(*args, **kwargs)

        #查询已经存在的地址
        s = T.select([T.news.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])

    #地址去重/过滤
    def link_screen(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        print('新页面:',len(new_links),'个-=-=-==-旧地址:',len(links)-len(new_links),'个')
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
        thetime = response.xpath('//a[@class="time"]/@data-created_at').extract()
        if(len(thetime)<1):
            thetime = response.xpath('//a[@class="edit-time"]/@data-created_at').extract()
        # thetime = wfunc.search_time(thetime)
        items['put_time'] = thetime[0].strip()
        url_re = re.search(r'.*\/(\d+)\/(\d+)$',response.url,re.I)
        items['url'] = response.url
        items['only_id'] = url_re.group(1)+url_re.group(2)
        items['body'] = response.xpath('//div[@class="article__bd__detail"]').extract()[0].strip()
        yield items

    #新浪股票新闻
    def parse_sina(self,response):
        # http://finance.sina.com.cn/stock/s/2017-11-06/doc-ifynmvuq9022743.shtml
        items = NewsItem()
        if(len(response.xpath('//title/text()').extract())>0):
            items['title'] = response.xpath('//title/text()').extract()[0].strip()
        else:
            items['title'] = ' '
        bodys = response.xpath('//div[@id="artibody"]//p').extract()            #得到的是列表
        body_str=''
        for ii in bodys:
            body_str+=ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'doc\-\D+(\d*)\.shtml',items['url'],re.I)
        items['only_id'] = url_re.group(1)
        thetime = response.xpath('//span[@class="time-source"]/text()').extract()[0].strip()
        items['put_time'] = wfunc.sina_get_time(thetime)
        yield items

    #腾讯证券快讯
    def parse_qq_ywq(self,response):
        # http://stock.qq.com/a/20171107/017324.htm
        items = NewsItem()
        items['title'] = response.xpath('//title/text()').extract()[0].strip()
        bodys = response.xpath('//div[@id="Cnt-Main-Article-QQ"]//p').extract()            #得到的是列表
        body_str=''
        for ii in bodys:
            body_str+=ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'.*a\/(\d+)\/(\d+).htm',items['url'],re.I)
        items['only_id'] = url_re.group(1)+url_re.group(2)
        thetime = response.xpath('//span[@class="a_time"]/text()').extract()[0].strip()
        if(not thetime):
            thetime = response.xpath('//span[@class="pubTime article-time"]/text()').extract()[0].strip()
        items['put_time'] = wfunc.time_num(thetime,"%Y-%m-%d %H:%M")
        yield items
