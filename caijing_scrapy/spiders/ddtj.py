#encoding:utf-8
# ###################################
# 新浪大单统计爬取
# by wooght
# 2017-11
# ###################################
import scrapy
from caijing_scrapy.settings import HEADERS
from caijing_scrapy.settings import USER_AGENT
from scrapy import Request
import numpy as np
import random
from caijing_scrapy.items import DdtjItem
import caijing_scrapy.model.Db as T
import time
import json

#历史行情查询 一只股票一行
class DdtjSpider(scrapy.Spider):
    name = 'ddtj'
    allowed_domains = ['sina.com.cn']
    start_urls = []
    url_module = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_Bill.GetBillSum?symbol=%s&num=60&sort=ticktime&asc=0&volume=0&amount=500000&type=0&day='
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,               #用scrapy自带的下载器中间件
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        "ITEM_PIPELINES" : {
           'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
        'LOG_LEVEL':'WARNING',
        'DOWNLOAD_DELAY' : 0.5,                                  #同一网站延迟时间
        'RANDOMIZE_DOWNLOAD_DELAY' : True                     #随机等待时间 在download-delay的基础上
    }
    HEADERS['User-Agent'] = random.choice(USER_AGENT)

    #查询地址生产器
    def __init__(self,codeid=None,*args,**kwargs):
        super(DdtjSpider,self).__init__(*args,**kwargs)
        if(codeid != None):
            s = T.select([T.listed_company.c.codeid,T.listed_company.c.shsz]).where(T.listed_company.c.codeid==codeid)
        else:
            s = T.select([T.listed_company.c.codeid,T.listed_company.c.shsz])
        r = T.conn.execute(s)
        for item in r.fetchall():
            id = self.builde_code(item[0],item[1])
            #调整编码长度
            print(id,'---')
            self.start_urls.append(self.url_module%(str(id)))
        print('共需查询:',len(self.start_urls),'支股票大单统计')
    # 股票代码生产
    def builde_code(self,id,zh):
        id = str(id)
        if(len(id)<6):
            while len(id)<6:
                id='0'+id
        id = zh+id
        return id
    #构建带头的请求
    def start_requests(self):
        total_date = np.arange(6)  #共查询最近6天大单记录
        nowtimes = int(time.time())
        for url in self.start_urls:
            for i in total_date:
                search_times = time.strftime("%Y-%m-%d",time.localtime(nowtimes-i*3600*24))
                newurl = url+str(search_times)
                yield Request(newurl,headers=HEADERS,callback=self.parse)
    def parse(self, response):
        items = DdtjItem()
        response_str = response.body
        response_str = response_str.decode('gbk').strip()
        pass_words = ['voltype','name','minvol','kevolume','keamount']
        if(response_str!='null'):
            item_str = response_str[2:-2].split(',')
            for item in item_str:
                sm_arr = item.split(':')
                if(sm_arr[0] not in pass_words):
                    key_name = sm_arr[0].strip("'")
                    if(key_name=='symbol'):
                        items['code_id'] = sm_arr[1].strip('"')[2:]
                    else:
                        items[key_name] = sm_arr[1].strip('"')
            items['only_id'] = items['opendate']+items['code_id']
            print(items['opendate'],items['code_id'])
            yield items
