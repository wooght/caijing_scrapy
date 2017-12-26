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
from caijing_scrapy.providers import wfunc
from caijing_scrapy.model.repository.quotes import Table_quotes
Q = Table_quotes()

#新浪大单爬取 最多查询最近11天
class DdtjSpider(scrapy.Spider):
    before_day = 8      #几天之前
    name = 'ddtj'
    allowed_domains = ['sina.com.cn']
    start_urls = []
    only_id = []
    nowtimes = int(time.time())
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
        'DOWNLOAD_DELAY' : 1,                                  #同一网站延迟时间
        'RANDOMIZE_DOWNLOAD_DELAY' : True                     #随机等待时间 在download-delay的基础上
    }
    HEADERS['User-Agent'] = random.choice(USER_AGENT)

    #查询地址生产器
    def __init__(self,codeid=None,*args,**kwargs):
        super(DdtjSpider,self).__init__(*args,**kwargs)
        total_date = self.total_data()
        if(codeid != None):
            r = Q.exists_quotes(id=int(codeid))
            p = T.select([T.ddtj.c.only_id]).where(T.ddtj.c.code_id==codeid)
        else:
            r = Q.exists_quotes()
            search_times = time.strftime("%Y-%m-%d",time.localtime(self.nowtimes-self.before_day*3600*24))   #载入指定时间的only_id
            p = T.select([T.ddtj.c.only_id]).where(T.ddtj.c.opendate>search_times)
        pr = T.conn.execute(p)
        for item in pr.fetchall():
            self.only_id.append(item[0])
        for item in r:
            code_id = item[0]
            shsz = 'sh' if code_id>=600000 else 'sz'
            id = wfunc.builde_code(item[0],shsz)
            code = str(id[2:])
            #只查询有行情存在的大单
            for d in item[1][:self.before_day]:
                only_id = d+code
                #只查询不存在的大单
                if(only_id not in self.only_id):
                    self.start_urls.append(self.url_module%(str(id))+str(d))

        print('共需查询:',len(self.start_urls),'支股票大单统计')

    #构建带头的请求
    def start_requests(self):
        total_date = self.total_data()
        for url in self.start_urls:
            print(url)
            yield Request(url,headers=HEADERS,callback=self.parse)

    #解析json
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

    #查询日期生产
    def total_data(self):
        total = np.arange(self.before_day)
        all_date = []
        for item in total:
            all_date.append(time.strftime("%Y-%m-%d",time.localtime(self.nowtimes-item*3600*24)))
        return all_date
