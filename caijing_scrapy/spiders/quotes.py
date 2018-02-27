# encoding:utf-8
#
# 网易历史行情抓取
# by wooght 2017-11
# 使用scrapy自带的下载中间件
#

import scrapy
from caijing_scrapy.settings import HEADERS
from caijing_scrapy.settings import USER_AGENT
from scrapy import Request
import random
from caijing_scrapy.items import QuotesItem, quotes_itemItem
from model import T
from factory.data_analyse import dd_pct
import time
import json
import common.wfunc


# 历史行情查询 一只股票一行
class Quotes_itemSpider(scrapy.Spider):
    name = 'quotes_item'
    allowed_domains = ['money.163.com/']
    start_urls = []
    url_module = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,  # 用scrapy自带的下载器中间件
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        "ITEM_PIPELINES": {
            'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
        'LOG_LEVEL': 'WARNING',
        # 'TELNETCONSOLE_PORT': '50855'
    }
    HEADERS['User-Agent'] = random.choice(USER_AGENT)

    # 查询地址生产器
    def __init__(self, codeid=None, first100=False, *args, **kwargs):
        super(Quotes_itemSpider, self).__init__(*args, **kwargs)
        self.select_data()

        if codeid == '0000001':  # 上证指数
            codes = [['0000001', 'szzs']]
        else:
            s = T.select([T.listed_company.c.codeid, T.listed_company.c.shsz])
            if first100:
                var_dd = dd_pct()
                var_dd.select_all(common.wfunc.before_day(80))
                code_100 = var_dd.have_dd(30)
                print(code_100)
                s = T.select([T.listed_company.c.codeid, T.listed_company.c.shsz]).where(
                    T.listed_company.c.codeid.in_(code_100))

            if codeid is not None:
                s = T.select([T.listed_company.c.codeid, T.listed_company.c.shsz]).where(
                    T.listed_company.c.codeid == codeid)
            r = T.conn.execute(s)
            codes = r.fetchall()
        for item in codes:
            id = self.builde_code(item[0], item[1])
            # 调整编码长度
            self.start_urls.append(self.url_module % (str(id), self.startdata, self.enddata))
        print('共需查询:' + str(len(self.start_urls)) + '支股票行情.......')

    # 股票代码生产
    def builde_code(self, id, zh):
        id = str(id)
        if (len(id) < 6):
            while len(id) < 6:
                id = '0' + id
            id = '1' + id
        elif (zh == 'sz'):
            id = '1' + id
        elif (zh == 'sh'):
            id = '0' + id
        return id

    # 构建带头的请求
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=HEADERS, callback=self.parse)

    def parse(self, response):
        items = quotes_itemItem()
        quotes = {}
        all_str = []
        csvstr = response.body  # 获取response返回的byte内容
        csvstr = csvstr.decode('gbk').strip()  # 编码转换
        csvlist = csvstr.split('\r\n')  # 分隔行
        csvlist = csvlist[1:]  # 删除第一行
        for item in csvlist:
            item = item.split(',')
            quotes['datatime'] = item[0]
            quotes['gao'] = item[4]
            quotes['kai'] = item[6]
            quotes['di'] = item[5]
            quotes['shou'] = item[3]
            quotes['before'] = item[7]
            quotes['zd_money'] = '0' if item[8] == 'None' else item[8]
            quotes['zd_range'] = '0' if item[9] == 'None' else item[9]
            quotes['liang'] = '0' if item[11] == 'None' else item[11]
            items['code_id'] = 1000001 if item[2].strip() == '上证指数' else item[1][1:]
            all_str.append(quotes)
            quotes = {}  # 元祖赋值后不能改变
        items['update_at'] = common.wfunc.today(strtime=False)
        items['quotes'] = json.dumps(all_str, ensure_ascii=False)
        try:
            print(':', items['code_id'], '抓取成功,保存中.....')
            yield items
        except KeyError as e:
            print(response.url, ',code_id error')

    # 构建查询时间
    def select_data(self):
        starttimes = int(time.time()) - 720 * 24 * 3600  # 一年
        self.startdata = time.strftime("%Y%m%d", time.localtime(starttimes))
        self.startdata = '20160201'  # 固定开始日期
        self.enddata = time.strftime("%Y%m%d", time.localtime())  # 当天


'''历史行情查询  一天一条'''


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['money.163.com/']
    start_urls = []
    url_module = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 543,  # 用scrapy自带的下载器中间件
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL': 'WARNING',
        'TELNETCONSOLE_PORT': '50855'
    }
    HEADERS['User-Agent'] = random.choice(USER_AGENT)

    # 查询地址生产器
    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.select_data()
        s = T.select([T.listed_company.c.codeid]).where(T.listed_company.c.codeid < 10)
        r = T.conn.execute(s)
        for item in r.fetchall():
            id = str(item[0])
            # 调整编码长度
            if (len(id) < 6):
                while len(id) < 6:
                    id = '0' + id
                id = '1' + id
            self.start_urls.append(self.url_module % (str(id), self.startdata, self.enddata))
        print('共需查询:', len(self.start_urls), '支股票行情.......')

    # 构建带头的请求
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=HEADERS, callback=self.parse)

    def parse(self, response):
        items = QuotesItem()
        csvstr = response.body  # 获取response返回的byte内容
        csvstr = csvstr.decode('gbk').strip()  # 编码转换
        csvlist = csvstr.split('\r\n')  # 分隔行
        csvlist = csvlist[1:]  # 删除第一行
        for item in csvlist:
            item = item.split(',')
            items['datatime'] = item[0]
            items['code_id'] = item[1][1:]  # 去除第一个引号
            items['gao'] = item[4]
            items['kai'] = item[6]
            items['di'] = item[5]
            items['shou'] = item[3]
            items['before'] = item[7]
            items['zd_money'] = '0' if item[8] == 'None' else item[8]
            items['zd_range'] = '0' if item[9] == 'None' else item[9]
            yield items

    # 构建查询时间
    def select_data(self):
        starttimes = int(time.time()) - 30 * 24 * 3600  # 30天
        self.startdata = time.strftime("%Y%m%d", time.localtime(starttimes))
        self.enddata = time.strftime("%Y%m%d", time.localtime())  # 当天

    # 调式用到的方法总结 设计到csv和文件读写问题
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
