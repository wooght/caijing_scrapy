# -*- coding: utf-8 -*-

#
#     第一财经-新闻,腾讯证券,新浪股票,自选股API爬取
#     by wooght 2017-10
#
import scrapy
from scrapy.http import Request
import re
from caijing_scrapy.items import NewsItem
from common import wfunc
from model import T
import json

# 以下两项 是spider拥有链接管理和追踪功能
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class NewsSpider(CrawlSpider):
    name = 'news'
    allowed_domains = ['yicai.com', 'sina.com.cn', 'qq.com', '163.com']
    download_delay = 0.5  # 设置下载延时
    start_urls = [
        'http://stock.qq.com/l/stock/ywq/list20150423143546.htm',
        'http://money.163.com/',
        'http://money.163.com/stock/',
        'http://finance.sina.com.cn/stock/',
        'http://www.yicai.com/data/',
        'http://www.yicai.com/news/comment/',
        'http://www.yicai.com/news/gushi/',
        'http://www.yicai.com/news/hongguan/',
        # 自选股新闻API
        'http://183.57.48.75/ifzqgtimg/appstock/news/yaowen/get?nkey=getQQNewsIndexAndItemsVerify&returnType=0,1,6,100,102&ids=&_columnId=stock_yaowen_v2_new&check=1&app=3G&_rndtime=1512981869&_appName=ios&_dev=iPhone8,2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3&_uin=10000&_wxuin=20000'
    ]
    # 自选股文章API模型
    url_models = 'http://183.57.48.75/ifzqgtimg/appstock/news/NewsOpenProxy/get?nkey=getQQNewsSimpleHtmlContentVerify' \
                 '&id=%s&chlid=news_news_istock&return=0,1,6,100,' \
                 '102&devid=b7f6945c2c01d5275408b475f9d3d77deccf4fce&appver=iphone5.8.1&_omgid' \
                 '=7f37d4eaf6195b4505da3fa034f73aacf580001011161c&_columnId=stock_yaowen_v2_new&_rndtime=1512996494' \
                 '&_appName=ios&_dev=iPhone8,' \
                 '2&_devId=b7f6945c2c01d5275408b475f9d3d77deccf4fce&_appver=5.8.1&_ifChId=&_isChId=1&_osVer=10.3.3' \
                 '&_uin=10000&_wxuin=20000 '

    rules = (
        # 新浪股票新闻 http://finance.sina.com.cn/stock/hyyj/2017-11-06/doc-ifynmnae234
        Rule(LinkExtractor(allow=(r'\D*finance\.sina\D*\/\d*\-\d*\-\d*\/doc\-\D*\d*\.shtml$',),
                           deny_domains=['qq.com', '163.com']), callback='parse_sina', follow=True,
             process_links='link_screen'),
        # 第一财经
        Rule(LinkExtractor(allow=('http\:\/\/www\.yicai\.com\/news\/\d+\.html',)), callback='parse_yicai', follow=False,
             process_links='link_screen'),
        # 腾讯证券 http://stock.qq.com/a/20171107/017324.htm
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/a\/\d+\/\d+\.htm$',),
                           deny_domains=['sina.com.cn', '163.com', 'yicai.com']), callback='parse_qq_ywq', follow=False,
             process_links='link_screen'),
        # http://stock.qq.com/l/stock/ywq/list20150423143546_2.htm 只查询前9页数据
        Rule(LinkExtractor(allow=('.*stock\.qq\.com\/.*\/list\d\_\d+.htm',)), follow=True, process_links='link_screen',
             process_request='wnews_request'),
        # process_request 指定对请求进行处理函数
        # 网易财经 http://money.163.com/17/1114/13/D375MGIB0025814V.html
        Rule(LinkExtractor(allow=('.*\.163\.com\/\d+\/\d+\/\d+\/.*\.html$',)), callback='parse_163_money', follow=True,
             process_links='link_screen'),

        # LinkExtractor(allow=('\/\d+\/\d+',),deny=('.*\.sina.*','.*\.htm',',*\.qq.*'),restrict_xpaths=('//div[@id="id"]/a')) LinkExtractor通过xpaths指定搜索范围
    )
    old_link = []

    # 动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,  # 处理普通静态页面
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL': 'WARNING'
    }

    # 自选股新闻API接口headers
    api_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-cn',
        'User-Agent': 'QQStock/17082410 CFNetwork/811.5.4 Darwin/16.7.0',
        'Referer': 'http://zixuanguapp.finance.qq.com',
        "Connection": "keep-alive",
        "Host": "183.57.48.75",
    }
    # 自选股新闻列表headers
    api_headers_index = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-cn',
        'User-Agent': 'QQStock/17082410 CFNetwork/811.5.4 Darwin/16.7.0',
        'Referer': 'http://zixuanguapp.finance.qq.com',
        "Connection": "keep-alive",
    }

    def __init__(self, *args, **kwargs):
        # 调用父类沟站函数
        super(NewsSpider, self).__init__(*args, **kwargs)

        # 查询已经存在的地址
        s = T.select([T.news.c.url])
        r = T.conn.execute(s)
        arr = r.fetchall()
        for one in arr:
            self.old_link.append(one[0])

    # 地址去重/过滤
    # must return dict
    def link_screen(self, links):
        new_links = []
        for i in links:
            if i.url not in self.old_link:
                new_links.append(i)
                self.old_link.append(i.url)
        print('news urls:', len(new_links), ' -=-=-==-old urls:', len(links) - len(new_links))
        return new_links

    # 首页处理,入口页面处理
    def parse_start_url(self, response):
        pass

    # 入口网页构建带参数request
    def start_requests(self):
        for url in self.start_urls:
            if '183.57.48.75' not in url:
                yield Request(url, meta={'phantomjs': True}, callback=self.parse)
            else:
                R = Request(url=url, callback=self.parse_zxg_index, headers=self.api_headers_index, dont_filter=True)
                yield R

    # 自选股新闻列表API
    def parse_zxg_index(self, response):
        response_json = self.get_json(response)
        ids = response_json['data']['ids']
        print(ids)
        for id in ids:
            if ('STO' in id):
                continue
            url = self.url_models % (id)
            R = Request(url=url, callback=self.parse_zxg_apinews, headers=self.api_headers, dont_filter=True)
            yield R

    # 自选股新闻API
    def parse_zxg_apinews(self, response):
        items = NewsItem()
        api = self.get_json(response)
        items['title'] = api['data']['title']
        items['only_id'] = api['data']['id']
        items['body'] = api['data']['content']['text']
        items['put_time'] = wfunc.time_num(api['data']['id'][:8], "%Y%m%d")
        items['url'] = api['data']['surl']
        yield items

    # 新地址构建request 带参数
    # must return Requets/None/Item
    def wnews_request(self, wrequests):
        print('new request run....', wrequests.url)
        r = scrapy.Request(wrequests.url, callback=self.parse)
        r.meta['phantomjs'] = True
        return r

    # 第一财经
    def parse_yicai(self, response):
        items = NewsItem()
        items['title'] = response.xpath('//head/title/text()').extract()[0].strip()
        thetime = response.xpath('//div[@class="m-title f-pr"]/h2//span[2]/text()').extract()[0].strip()
        items['put_time'] = wfunc.time_num(thetime, "%Y-%m-%d %H:%M")
        items['url'] = response.url
        h_num = re.search(r'\/(\d+)\.html', items['url'], re.I).group(1)
        items['only_id'] = h_num
        items['body'] = response.xpath('//div[@class="m-text"]').extract()[0].strip()
        wfunc.e('yicai_news:'+items['title'])
        yield items

    # 新浪股票新闻
    def parse_sina(self, response):
        # http://finance.sina.com.cn/stock/s/2017-11-06/doc-ifynmvuq9022743.shtml
        items = NewsItem()
        if len(response.xpath('//title/text()').extract()) > 0:
            items['title'] = response.xpath('//title/text()').extract()[0].strip()
        else:
            items['title'] = ' '
        bodys = response.xpath('//div[@id="artibody"]//p').extract()  # 得到的是列表
        body_str = ''
        for ii in bodys:
            body_str += ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'doc\-\D+(\d*)\.shtml', items['url'], re.I)
        items['only_id'] = url_re.group(1)
        thetime = response.xpath('//span[@class="time-source"]/text()').extract()[0].strip()
        items['put_time'] = wfunc.sina_get_time(thetime)
        wfunc.e('sina_news:' + items['title'])
        yield items

    # 腾讯证券快讯
    def parse_qq_ywq(self, response):
        # http://stock.qq.com/a/20171107/017324.htm
        items = NewsItem()
        items['title'] = response.xpath('//title/text()').extract()[0].strip()
        bodys = response.xpath('//div[@id="Cnt-Main-Article-QQ"]//p').extract()  # 得到的是列表
        body_str = ''
        for ii in bodys:
            body_str += ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'.*a\/(\d+)\/(\d+).htm', items['url'], re.I)
        items['only_id'] = url_re.group(1) + url_re.group(2)
        thetime = response.xpath('//span[@class="a_time"]/text()')
        if (len(thetime) < 1):
            thetime = response.xpath('//span[@class="pubTime article-time"]/text()')
        try:
            items['put_time'] = wfunc.time_num(thetime.extract()[0].strip(), "%Y-%m-%d %H:%M")
        except IndexError as e:
            print('IndexError:dont fond time-->', response.url)
            return None
        wfunc.e('qq_news:' + items['title'])
        yield items

    # 网易财经新闻
    def parse_163_money(self, response):
        # http://money.163.com/17/1114/13/D375MGIB0025814V.html
        items = NewsItem()
        items['title'] = response.xpath('//div[@id="epContentLeft"]/h1[1]/text()').extract()[0].strip()
        bodys = response.xpath('//div[@id="endText"]//p').extract()
        body_str = ''
        for ii in bodys:
            body_str += ii.strip()
        items['body'] = body_str
        items['url'] = response.url
        url_re = re.search(r'.*\.163\.com\/\d+\/\d+\/\d+\/(\w*)\.html$', items['url'], re.I)
        items['only_id'] = url_re.group(1)
        thetime = response.xpath('//div[@class="post_time_source"]/text()').extract_first().strip()
        items['put_time'] = wfunc.time_num(thetime[:16], "%Y-%m-%d %H:%M")
        wfunc.e('163_news:' + items['title'])
        yield items

    def get_json(self, str):
        response_str = str.body.decode('utf-8')
        response_json = json.loads(response_str, encoding='utf8')
        return response_json
