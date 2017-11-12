#encoding:utf-8
#
# 网易历史行情抓取
# by wooght 2017-11
#

import scrapy
from caijing_scrapy.settings import HEADERS
from caijing_scrapy.settings import USER_AGENT
from scrapy import Request
import random
import csv
from caijing_scrapy.items import QuotesItem
import caijing_scrapy.Db as T
import time
import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码from scrapy import Request


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['money.163.com/']
    start_urls = []
    url_module = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,
           'caijing_scrapy.middlewares.middlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL':'WARNING',
        'TELNETCONSOLE_PORT':'50855'
    }
    HEADERS['User-Agent'] = random.choice(USER_AGENT)

    #查询地址生产器
    def __init__(self,*args,**kwargs):
        super(QuotesSpider,self).__init__(*args,**kwargs)
        self.select_data()
        s = T.select([T.listed_company.c.codeid]).where(T.listed_company.c.codeid<1000000)
        r = T.conn.execute(s)
        for item in r.fetchall():
            id = str(item[0])
            #调整编码长度
            if(len(id)<6):
                while len(id)<6:
                    id='0'+id
                id='1'+id
            self.start_urls.append(self.url_module%(str(id),self.startdata,self.enddata))
        print('共需查询:',len(self.start_urls),'支股票行情.......')

    #构建带头的请求
    def start_requests(self):
        for url in self.start_urls:
            print('查询:',url)
            yield Request(url,headers=HEADERS,callback=self.parse)

    def parse(self, response):
        items = QuotesItem()
        csvstr = response.body                      #获取response返回的byte内容
        csvstr = csvstr.decode('gbk').strip()       #编码转换
        csvlist = csvstr.split('\r\n')              #分隔行
        csvlist = csvlist[1:]                       #删除第一行
        for item in csvlist:
            item=item.split(',')
            items['datatime'] = item[0]
            items['code_id'] = item[1][1:]          #去除第一个引号
            items['gao'] = item[4]
            items['kai'] = item[6]
            items['di'] = item[5]
            items['shou'] =item[3]
            items['before'] = item[7]
            items['zd_money'] = '0' if item[8]=='None' else item[8]
            items['zd_range'] = '0' if item[9]=='None' else item[9]
            yield items

    #构建查询时间
    def select_data(self):
        starttimes = int(time.time())-30*24*3600    #30天
        self.startdata = time.strftime("%Y%m%d",time.localtime(starttimes))
        self.enddata = time.strftime("%Y%m%d",time.localtime())  #当天


    #调式用到的方法总结 设计到csv和文件读写问题
    # def parse(self, response):
    #     items = QuotesItem()
    #     # file = open('hah.csv','w',encoding='utf-8')
    #     # file.write(str(response.body.decode('gbk')))
    #     csv_file = response.body.decode('gbk').strip()
    #     csv_file = csv_file.split('\r\n')
    #     print(csv_file)
    #     csv_str = csv.reader(open('hah.csv','r',encoding='utf-8'))  #指定编码打开文件
    #     csv_str = csv.reader(csv_file,dialect='excel-tab',delimiter=',')
    #     for item in csv_str:
    #         print(item,'-=-=')
    #     yield None
