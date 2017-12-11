# -*- coding: utf-8 -*-
#
# 新闻抓取保存
# by wooght 2017-11

from caijing_scrapy.items import NewsItem,TopicItem,CodesItem,QuotesItem,PlatesItem,NoticesItem,QandaItem
import caijing_scrapy.model.Db as T
import caijing_scrapy.providers.wfunc as wfunc
from caijing_scrapy.analyse.pipeline_article_analyse import article_analyse
import time

class CaijingScrapyPipeline(object):
    def __init__(self,*args,**kwargs):
        super(CaijingScrapyPipeline,self).__init__(*args,**kwargs)
        self.article_analyse = article_analyse()
        self.add_nums = 0
        self.min_time = time.time()-90*24*3600  #只提取三个月内的数据
        wfunc.e('analyse new success!')
    def open_spider(self,spider):
        wfunc.e('spider '+spider.name+' --->opend')

    def add_attitude_relation(self,item):
        if(len(item)>0):
            i = T.attitude_relation.insert()
            r = T.conn.execute(i,item)

    def process_item(self, item, spider):
        if('put_time' in dict(item)):
            if(float(item['put_time'])<self.min_time):
                return None
        self.add_nums+=1
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
            #语义分析
            att_item = item
            att_item['article_id'] = r.inserted_primary_key
            att_item['article_type'] = 2
            result = self.article_analyse.run(att_item)
            self.add_attitude_relation(result)
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
            #语义分析
            att_item = item
            att_item['article_id'] = r.inserted_primary_key
            att_item['article_type'] = 1
            result = self.article_analyse.run(att_item)
            self.add_attitude_relation(result)

        #股票代码
        elif(isinstance(item,CodesItem)):
            if(spider.name=='codes'):
                s = T.select([T.listed_company]).where(T.listed_company.c.codeid==item['codeid'])
                r = T.conn.execute(s)
                if(r.rowcount>0):
                    return None
                i = T.listed_company.insert()
                r = T.conn.execute(i,dict(item))
            elif(spider.name=='upplates'):
                u = T.listed_company.update().where(T.listed_company.c.codeid==item['codeid']).values(plate_id=item['plate_id'])
                r = T.conn.execute(u)

        #股票行情
        elif(isinstance(item,QuotesItem)):
            i = T.quotes.insert()
            r = T.conn.execute(i,dict(item))

        #股票板块
        elif(isinstance(item,PlatesItem)):
            s = T.select([T.listed_plate]).where(T.listed_plate.c.plateid==item['plateid'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.listed_plate.insert()
            r = T.conn.execute(i,dict(item))

        #公司公告
        elif(isinstance(item,NoticesItem)):
            s = T.select([T.company_notice]).where(T.company_notice.c.title==item['title']).where(T.company_notice.c.code_id==item['code_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.company_notice.insert()
            r = T.conn.execute(i,dict(item))

        #问答
        elif(isinstance(item,QandaItem)):
            s = T.select([T.qanda.c.id]).where(T.qanda.c.only_id==item['only_id'])
            r = T.conn.execute(s)
            if(r.rowcount>0):
                return None
            i = T.qanda.insert()
            r = T.conn.execute(i,dict(item))

        return None

    def close_spider(self,spider):
        wfunc.e('spider '+spider.name+' --->closed')
        wfunc.e('add total nums :'+str(self.add_nums))
