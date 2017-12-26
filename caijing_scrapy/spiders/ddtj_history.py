# -*- coding: utf-8 -*-
##########################################
# 历史大单统计
# 历史成交明细爬取 新浪
# by Wooght
# date 2017-12-25
# ########################################
#
import scrapy
from scrapy.http import Request
import re
import time
from caijing_scrapy.items import DdtjItem
import caijing_scrapy.providers.wfunc as wfunc
from model import *
import json

class DetailsSpider(scrapy.Spider):
    name = 'ddtj_history'
    url_models = 'http://market.finance.sina.com.cn/downxls.php?date=%s&symbol=%s'
    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,           #处理普通静态页面
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL':'WARNING',
        'RETRY_TIMES' : 2,#访问超时 重新访问的次数
        "ITEM_PIPELINES" : {
           'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
        'CONCURRENT_REQUESTS_PER_DOMAIN':8,
    }
    ddtj_onlyid = []

    #构建查询code_id及查询日期--->根据行情构建有效日期
    def select_quotes(self):
        r = T.select([T.quotes_item.c.quotes,T.quotes_item.c.code_id])
        s = T.conn.execute(r)
        code = []
        for quotes in s.fetchall():
            quotes_json = json.loads(quotes[0])
            one = []
            one.append(quotes[1])
            opendate = []
            for dateitem in quotes_json:
                if(float(dateitem['shou'])>0):
                    #行情收大于0 没停盘的才有效
                    opendate.append(dateitem['datatime'])
            one.append(opendate)
            code.append(one)
        return code

    #查询only_id 以便去重
    def select_onlyid(self):
        s = T.select([T.ddtj.c.only_id])
        r = T.conn.execute(s)
        ddtj_onlyid = []
        for item in r.fetchall():
            ddtj_onlyid.append(item[0])
        self.ddtj_onlyid = ddtj_onlyid

    def start_requests(self):
        self.select_onlyid()
        code = self.select_quotes()
        for cp in code:
            code_id = cp[0]
            for dt in cp[1]:
                shsz = 'sh' if code_id>=600000 else 'sz'
                id = wfunc.builde_code(code_id,shsz) #调整编码长度
                only_id = dt+str(id[2:])
                if(only_id in self.ddtj_onlyid):
                    print('is exists...')
                    #重复only_id跳过
                    continue
                url = self.url_models%(dt,id)
                R = Request(url,meta={'code_id':code_id,'opendate':dt,'only_id':only_id},callback=self.parse)
                yield R

    def parse(self,response):
        items = DdtjItem()
        quotes = {}
        all_str = []
        csvstr = response.body                      #获取response返回的byte内容
        csvstr = csvstr.decode('gbk').strip()       #编码转换
        csvlist = csvstr.split('\n')                #分隔行
        csvlist = csvlist[1:]                       #删除第一行
        if(len(csvlist)>100):
            items = self.editor_data(csvlist,items)
            items['only_id'] = response.meta['only_id']
            items['opendate'] = response.meta['opendate']
            items['code_id'] = response.meta['code_id']
            #一股等于100手
            items['kuvolume'] = items['kuvolume']*100
            items['kdvolume'] = items['kdvolume']*100
            items['totalvol'] = items['totalvol']*100
            print(items)
            yield items

    #数据处理
    def editor_data(self,csvdata,items):
        items['kdvolume'] = 0
        items['kuvolume'] = 0
        zxvolume = 0
        items['kdamount'] = 0
        items['kuamount'] = 0
        zxamount = 0
        items['stockamt'] = 0
        items['stockvol'] = 0
        items['totalvolpct'] = 0
        items['totalamtpct'] = 0
        items['totalvol'] = 0
        items['totalamt'] = 0
        for i in csvdata:
            itemlist = i.split('\t')
            #大单量设置为500000成交额
            if(int(itemlist[4])>=500000):
                if(itemlist[5]=='中性盘'):
                    zxvolume+=int(itemlist[3])
                    zxamount+=int(itemlist[4])
                elif(itemlist[5]=='买盘'):
                    items['kuvolume']+=int(itemlist[3])
                    items['kuamount']+=int(itemlist[4])
                elif(itemlist[5]=='卖盘'):
                    items['kdvolume']+=int(itemlist[3])
                    items['kdamount']+=int(itemlist[4])
            items['totalvol'] = items['kuvolume']+items['kdvolume']
            items['totalamt'] = items['kuamount']+items['kdamount']
            items['stockamt']+=int(itemlist[4])
            items['stockvol']+=int(itemlist[3])
        totalamtpct=(items['kuamount']+items['kdamount']+zxamount)/items['stockamt']
        items['totalamtpct'] = '%0.2f'%totalamtpct
        totalvolpct=(items['kuvolume']+items['kdvolume']+zxvolume)/items['stockvol']
        items['totalvolpct'] = '%0.2f'%totalvolpct
        return items
