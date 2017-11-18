# -*- coding: utf-8 -*-

#
#     第一财经-新闻,腾讯证券,新闻股票
#     by wooght 2017-10
#
import scrapy
from scrapy.http import Request
import re
import time
from caijing_scrapy.items import NewsItem
import caijing_scrapy.providers.wfunc as wfunc

import caijing_scrapy.Db as T

#以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

def wnews_request(x):
    print('-=-=-=-=-=-=-=>',x)

class NewsSpider(CrawlSpider):
    name = 'news'
    allowed_domains = ['www.yicai.com','sina.com.cn','qq.com','163.com']
    download_delay = 1                                              #设置下载延时
    start_urls = [
                    # 'http://www.yicai.com/news/5365720.html',
                    # 'https://xueqiu.com/7859591518/95051267',
                    # 'http://finance.sina.com.cn/stock/s/2017-11-06/doc-ifynmvuq9022743.shtml'

                    'http://stock.qq.com/l/stock/ywq/list20150423143546.htm',
                    'http://money.163.com/',
                    'http://money.163.com/stock/',
                    'http://finance.sina.com.cn/stock/',
                    'http://www.yicai.com/data/',
                    'http://www.yicai.com/news/comment/',
                    'http://www.yicai.com/news/gushi/',
                    'http://www.yicai.com/news/hongguan/',

                 ]

    rules = (
        # 新浪股票新闻 http://finance.sina.com.cn/stock/hyyj/2017-11-06/doc-ifynmnae234
        Rule(LinkExtractor(allow=(r'\D*finance\.sina\D*\/\d*\-\d*\-\d*\/doc\-\D*\d*\.shtml$',),deny_domains=['qq.com','163.com']),callback='parse_sina',follow=True,process_links='link_screen'),
        #第一财经
        Rule(LinkExtractor(allow=('http\:\/\/www\.yicai\.com\/news\/\d+\.html',)),callback='parse_yicai',follow=True,process_links='link_screen'),
        #腾讯证券 http://stock.qq.com/a/20171107/017324.htm
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/a\/\d+\/\d+\.htm$',),deny_domains=['sina.com.cn','163.com','yicai.com']),callback='parse_qq_ywq',follow=False,process_links='link_screen'),
        # http://stock.qq.com/l/stock/ywq/list20150423143546_2.htm
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/.*\/list\d+\_\d+.htm',)),follow=True,process_links='link_screen',process_request='wnews_request'),
        # process_request 指定对请求进行处理函数
        #网易财经 http://money.163.com/17/1114/13/D375MGIB0025814V.html
        Rule(LinkExtractor(allow=('.*\.163\.com\/\d+\/\d+\/\d+\/.*\.html$',)),callback='parse_163_money',follow=True,process_links='link_screen'),

        # LinkExtractor(allow=('\/\d+\/\d+',),deny=('.*\.sina.*','.*\.htm',',*\.qq.*'),restrict_xpaths=('//div[@id="id"]/a')) LinkExtractor通过xpaths指定搜索范围
    )
    old_link = []

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,           #处理普通静态页面
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL':'WARNING'
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
    #must return dict
    def link_screen(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        print('news urls:',len(new_links),' -=-=-==-old urls:',len(links)-len(new_links))
        return new_links

    #首页处理,入口页面处理
    def parse_start_url(self,response):
        pass
    #入口网页构建带参数request
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,meta={'phantomjs':True},callback=self.parse)

    #新地址构建request 带参数
    #must return Requets/None/Item
    def wnews_request(self,wrequests):
        print('new request run....',wrequests.url)
        r = scrapy.Request(wrequests.url,callback=self.parse)
        r.meta['phantomjs'] = True
        return r

    #第一财经
    def parse_yicai(self,response):
        items = NewsItem()
        items['title'] = response.xpath('//head/title/text()').extract()[0].strip()
        thetime = response.xpath('//div[@class="m-title f-pr"]/h2//span[2]/text()').extract()[0].strip()
        items['put_time'] = wfunc.time_num(thetime,"%Y-%m-%d %H:%M")
        items['url'] = response.url
        h_num = re.search(r'\/(\d+)\.html',items['url'],re.I).group(1)
        items['only_id'] = h_num
        items['body'] = response.xpath('//div[@class="m-text"]').extract()[0].strip()
        print(items['put_time'])
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
        thetime = response.xpath('//span[@class="a_time"]/text()')
        if(len(thetime)<1):
            thetime = response.xpath('//span[@class="pubTime article-time"]/text()')
        try:
            items['put_time'] = wfunc.time_num(thetime.extract()[0].strip(),"%Y-%m-%d %H:%M")
        except IndexError as e:
            print('IndexError:dont fond time-->',response.url)
            return None
        print(response.url,'-->seccess')
        yield items

    #网易财经新闻
    def parse_163_money(self,response):
        # http://money.163.com/17/1114/13/D375MGIB0025814V.html
        items = NewsItem()
        items['title'] = response.xpath('//div[@id="epContentLeft"]/h1[1]/text()').extract()[0].strip()
        bodys = response.xpath('//div[@id="endText"]//p').extract()
        body_str=''
        for ii in bodys:
            body_str+=ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'.*\.163\.com\/\d+\/\d+\/\d+\/(\w*)\.html$',items['url'],re.I)
        items['only_id'] = url_re.group(1)
        thetime = response.xpath('//div[@class="post_time_source"]/text()').extract_first().strip()
        print(thetime[:16],',',items['only_id'])
        items['put_time'] = wfunc.time_num(thetime[:16],"%Y-%m-%d %H:%M")
        yield items
