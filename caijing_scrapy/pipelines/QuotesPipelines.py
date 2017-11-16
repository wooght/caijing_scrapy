# -*- coding: utf-8 -*-
#
# 行情抓取保存 行
# by wooght 2017-11

from caijing_scrapy.items import quotes_itemItem
import caijing_scrapy.Db as T
import caijing_scrapy.providers.wfunc as wfunc

class Pipeline(object):
    def open_spider(self,spider):
        print(spider.name,'--->start============>>>>>')

    def process_item(self, item, spider):
        if(isinstance(item,quotes_itemItem)):
            s = T.quotes_item.delete().where(T.quotes_item.c.code_id==item['code_id'])
            r = T.conn.execute(s)
            i = T.quotes_item.insert()
            r = T.conn.execute(i,dict(item))

        return None

    def close_spider(self,spider):
        print(spider.name,'--->closed========>>>>>>>>>>')
