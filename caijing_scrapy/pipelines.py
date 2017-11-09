# -*- coding: utf-8 -*-
#
# 新闻抓取保存
# by wooght 2017-11

from caijing_scrapy.items import NewsItem,TopicItem
import caijing_scrapy.Db as T

class CaijingScrapyPipeline(object):
    def open_spider(self,spider):
        print(spider.name,'--->open============>>>>>')

    def process_item(self, item, spider):
        #新闻文章
        if(isinstance(item,NewsItem)):
            s = T.select([T.news]).where(T.news.c.only_id==item['only_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.news.insert()
            r = T.conn.execute(i,dict(item))
        #专题分析文章
        elif(isinstance(item,TopicItem)):
            s = T.select([T.topic]).where(T.topic.c.only_id==item['only_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.topic.insert()
            r = T.conn.execute(i,dict(item))

        return None

    def close_spider(self,spider):
        print(spider.name,'--->close========>>>>>>>>>>')
