# -*- coding: utf-8 -*-
#
# 新闻抓取保存
# by wooght 2017-11

from caijing_scrapy.items import NewsItem,TopicItem,CodesItem,QuotesItem
import caijing_scrapy.Db as T
import caijing_scrapy.providers.wfunc as wfunc

class CaijingScrapyPipeline(object):
    def open_spider(self,spider):
        print(spider.name,'--->open============>>>>>')

    def process_item(self, item, spider):
        #新闻文章
        if(isinstance(item,NewsItem)):
            #去除body中的html标签
            item['body'] = wfunc.delete_html(item['body'])
            s = T.select([T.news]).where(T.news.c.only_id==item['only_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.news.insert()
            r = T.conn.execute(i,dict(item))
        #专题分析文章
        elif(isinstance(item,TopicItem)):
            #去除body中的html标签
            item['body'] = wfunc.delete_html(item['body'])
            s = T.select([T.topic]).where(T.topic.c.only_id==item['only_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.topic.insert()
            r = T.conn.execute(i,dict(item))
        elif(isinstance(item,CodesItem)):
            s = T.select([T.listed_company]).where(T.listed_company.c.codeid==item['codeid'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.listed_company.insert()
            r = T.conn.execute(i,dict(item))
        elif(isinstance(item,QuotesItem)):
            i = T.quotes.insert()
            r = T.conn.execute(i,dict(item))

        return None

    def close_spider(self,spider):
        print(spider.name,'--->close========>>>>>>>>>>')
