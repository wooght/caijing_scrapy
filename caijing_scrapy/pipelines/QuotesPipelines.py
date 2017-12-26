# -*- coding: utf-8 -*-
#
# 行情抓取保存 行
# by wooght 2017-11

from caijing_scrapy.items import quotes_itemItem,DdtjItem,ZuheItem, ZhchangeItem
from model import T


class Pipeline(object):
    add_nums = 0
    def open_spider(self,spider):
        print(spider.name,'--->start============>>>>>')
        if(spider.name in ['ddtj','detailshistory']):
            s = T.select([T.ddtj.c.only_id])
            r = T.conn.execute(s)
            ddtj_onlyid = []
            for item in r.fetchall():
                ddtj_onlyid.append(item[0])
            self.ddtj_onlyid = ddtj_onlyid
        if(spider.name=='xueqiu_zuhe'):
            s = T.select([T.xq_zuhe.c.zh_symbol])
            r = T.conn.execute(s)
            zh_list=[]
            for item in r.fetchall():
                zh_list.append(item[0])
            self.zh_list = zh_list
        if(spider.name=='zuhe_change'):
            s = T.select([T.zuhe_change.c.change_id])
            r = T.conn.execute(s)
            change_list=[]
            for item in r.fetchall():
                change_list.append(item[0])
            self.change_list = change_list

    def process_item(self, item, spider):
        #行情
        if(isinstance(item,quotes_itemItem)):
            s = T.quotes_item.delete().where(T.quotes_item.c.code_id==item['code_id'])
            r = T.conn.execute(s)
            i = T.quotes_item.insert()
            r = T.conn.execute(i,dict(item))
        #大单
        elif(isinstance(item,DdtjItem)):
            if(item['only_id'] not in self.ddtj_onlyid):
                i = T.ddtj.insert()
                r = T.conn.execute(i,dict(item))
        #组合
        elif(isinstance(item,ZuheItem)):
            if(item['zh_symbol'] not in self.zh_list):
                i = T.xq_zuhe.insert()
                r = T.conn.execute(i,dict(item))
        #组合条仓
        elif(isinstance(item,ZhchangeItem)):
            if(item['change_id'] not in self.change_list):
                i = T.zuhe_change.insert()
                r = T.conn.execute(i,dict(item))
        return None

    def close_spider(self,spider):
        print(spider.name,'--->closed========>>>>>>>>>>')
