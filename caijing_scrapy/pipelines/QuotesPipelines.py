# -*- coding: utf-8 -*-
#
# 行情抓取保存 行
# by wooght 2017-11

from caijing_scrapy.items import quotes_itemItem,DdtjItem
import caijing_scrapy.model.Db as T
import caijing_scrapy.providers.wfunc as wfunc

class Pipeline(object):
    def open_spider(self,spider):
        print(spider.name,'--->start============>>>>>')
        s = T.select([T.ddtj.c.only_id])
        r = T.conn.execute(s)
        ddtj_onlyid = []
        for item in r.fetchall():
            ddtj_onlyid.append(item[0])
        self.ddtj_onlyid = ddtj_onlyid

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
        return None

    def close_spider(self,spider):
        print(spider.name,'--->closed========>>>>>>>>>>')
