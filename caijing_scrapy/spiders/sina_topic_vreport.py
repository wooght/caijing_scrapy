# -*- coding: utf-8 -*-
#
# ##################################
# 新浪研究报告爬取
# by Wooght
# 2017-11
# ##################################
import scrapy
import re
import time
from caijing_scrapy.items import TopicItem
import caijing_scrapy.providers.wfunc as wfunc
import numpy as np
import caijing_scrapy.Db as T

#以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

class TopicVreport(CrawlSpider):
    name = 'vreport_topics'
    allowed_domains = ['sina.com.cn']
    to_continue = True #是否继续爬取
    start_urls = [
                    #新浪研究报告之-研究机构
                    'http://vip.stock.finance.sina.com.cn/q/go.php/vReport_Show/kind/search/rptid/4008645/index.phtml',
                 ]
    rules = (
        #研究机构文章
        #http://vip.stock.finance.sina.com.cn/q/go.php/vReport_Show/kind/search/rptid/4008645/index.phtml
        Rule(LinkExtractor(allow=('\/\d+\/index\.phtml$',),deny=('.*\.jrj.*','.*\.htm',',*\.shtml$')),callback='parse_vreport',follow=False,process_links='link_screen'),
    )
    old_link = []

    #动态修改配置内容
    custom_settings = {
        'LOG_LEVEL':'WARNING'
    }

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
        super(TopicVreport,self).__init__(*args, **kwargs)

        #查询已经存在的地址
        s = T.select([T.topic.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])

    def parse_start_url(self,response):
        pass

    def start_requests(self):
        total_num = np.arange(1,50)
        for i in total_num:
            #如果没有更多 则停止爬取
            if(not self.to_continue): break
            url = "http://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/lastest/index.phtml?p=%d"%i
            print(url)
            r = scrapy.Request(url,callback=self.parse)
            r.meta['phantomjs'] = True
            yield r

    #地址去重/过滤
    def link_screen(self,links):
        new_links = []
        for i in links:
            if(i.url not in self.old_link):
                new_links.append(i)
                self.old_link.append(i.url)
        print('新页面:',len(new_links),'个-=-=-==-旧地址:',len(links)-len(new_links),'个')
        if(len(new_links)<1):
            self.to_continue = False
        return new_links

    #新浪机构研究报告
    def parse_vreport(self,response):
        items = TopicItem()
        items['title'] = response.xpath('//h1/text()').extract_first().strip()
        thetime = response.xpath('//div[@class="creab"]/span[4]/text()').extract()[0].strip()
        thetime = wfunc.time_num(thetime.split('：')[1],'%Y-%m-%d')
        items['put_time'] = thetime
        url_re = re.search(r'\/(\d+)\/index\.phtml$',response.url,re.I)
        items['url'] = response.url
        items['only_id'] = url_re.group(1)
        items['body'] = response.xpath('//div[@class="blk_container"]').extract()[0].strip()
        wfunc.e('xueqiu_topic:'+items['title'])
        yield items
