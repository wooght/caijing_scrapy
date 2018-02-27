# -*- coding: utf-8 -*-
# ####################################
# 雪球组合爬取
# 组合调仓爬取
# by Wooght
# 2017-12
# ####################################
import scrapy
from scrapy import Request
import json
from caijing_scrapy.items import ZuheItem, ZhchangeItem
from model import *
from numpy import arange


# 组合100强查询
# 一般两天更新一次
class XueqiuZuheSpider(scrapy.Spider):
    name = 'xueqiu_zuhe'
    allowed_domains = ['xueqiu.com']
    start_urls = ['https://xueqiu.com/']
    url_models = [
        'https://api.xueqiu.com/cubes/rank/arena_cubes.json?count=100&cube_level=3&list_param=list_overall&market=cn&page=1&_=1513064366380&_s=18b896',
        'https://api.xueqiu.com/cubes/rank/arena_cubes.json?count=100&cube_level=2&list_param=list_overall&market=cn&page=1&_=1513064366380&_s=18b896',
        'https://api.xueqiu.com/cubes/rank/arena_cubes.json?count=100&cube_level=1&list_param=list_overall&market=cn&page=1&_=1513064366380&_s=18b896',
    ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,  # 处理普通静态页面
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        "ITEM_PIPELINES": {
            'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
    }

    # 雪球组合api headers
    api_headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'User-Agent': 'Xueqiu iPhone 9.17',
        "Connection": "keep-alive",
        "Host": "api.xueqiu.com",
    }

    # 访问首页 获取cookie
    def parse(self, response):
        cookie = response.headers.getlist('Set-Cookie')
        r_cookie = {}
        for c in cookie:
            cc = c.decode('utf8')
            if ('xq_a_token' in cc and 'xq_a_token.sig' not in cc):
                cc_arr = cc.split(';')
                cc_nums = cc_arr[0][11:]
                r_cookie["xq_a_token"] = cc_nums
        r_cookie['u'] = '9333734819'
        for url in self.url_models:
            # 这里技巧  meta指向一个没有指定的cookie模块 及清空cookie  使用自定义的cookie
            R = Request(url=url, meta={'cookiejar': 2}, headers=self.api_headers, cookies=r_cookie,
                        callback=self.api_zuhe_parse)
            yield R

    def api_zuhe_parse(self, response):
        items = ZuheItem()
        result_str = response.body.decode('utf8')
        result_json = json.loads(result_str)
        zuhe_list = result_json['list']
        print(len(zuhe_list))
        for i in zuhe_list:
            items['zh_symbol'] = i['symbol']
            items['zh_id'] = i['id']
            items['owner_id'] = i['owner_id']
            items['zh_name'] = i['name']
            print(items, '--')
            yield items


# 组合调仓
# 每天更新
class ZhChangeSpider(scrapy.Spider):
    name = 'zuhe_change'
    allowed_domains = ['xueqiu.com']
    start_urls = ['https://xueqiu.com/']
    url_models = 'https://api.xueqiu.com/cubes/rebalancing/history.json?count=50&cube_symbol=%s&page=1&_=1513147084721&_s=b13051&_t=5AF984E4-D2CE-4728-85A9-178619CD9070.2174101414.1513147059112.1513147084723'
    url_model_page = 'https://api.xueqiu.com/cubes/rebalancing/history.json?count=50&cube_symbol=%s&page=%s&_=1513147084721&_s=b13051&_t=5AF984E4-D2CE-4728-85A9-178619CD9070.2174101414.1513147059112.1513147084723'
    zh_list = []
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,  # 处理普通静态页面
            'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        "ITEM_PIPELINES": {
            'caijing_scrapy.pipelines.QuotesPipelines.Pipeline': 300,
        },
    }

    # 雪球组合api headers
    api_headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'User-Agent': 'Xueqiu iPhone 9.17',
        "Connection": "keep-alive",
        "Host": "api.xueqiu.com",
        "Referer": ''
    }

    def __init__(self, *args, **kwargs):
        super(ZhChangeSpider, self).__init__(*args, **kwargs)
        # 查询所有组合symbol
        s = T.select([T.xq_zuhe.c.zh_symbol, T.xq_zuhe.c.id])  # .where(T.xq_zuhe.c.id<5)
        r = T.conn.execute(s)
        for i in r.fetchall():
            self.zh_list.append(i[0])

    # 访问首页 获取cookie
    def parse(self, response):
        cookie = response.headers.getlist('Set-Cookie')
        r_cookie = {}
        for c in cookie:
            cc = c.decode('utf8')
            if ('xq_a_token' in cc and 'xq_a_token.sig' not in cc):
                cc_arr = cc.split(';')
                cc_nums = cc_arr[0][11:]
                # r_cookie["xq_a_token"]=cc_nums
                r_cookie['xq_a_token'] = 'fb7d1602fbdfe5a615561428cdfb0d786d06cd34'
        r_cookie['u'] = '2174101414'
        self.r_cookie = r_cookie
        for symbol in self.zh_list:
            print(self.url_models % (symbol))
            R = Request(url=self.url_models % (symbol), meta={'cookiejar': 2, 'zh_symbol': symbol},
                        headers=self.api_headers, cookies=r_cookie, callback=self.api_zuhe_parse)
            yield R

    def api_zuhe_parse(self, response):
        items = ZhchangeItem()
        result_str = response.body.decode('utf8')
        result_json = json.loads(result_str)
        change_list = result_json['list']
        for i in change_list:
            # 调仓成功则记录
            if i['status'] == 'success':
                # 读取调仓股票列表
                for ci in i['rebalancing_histories']:
                    items['zh_symbol'] = response.meta['zh_symbol']
                    items['change_id'] = ci['id']
                    items['stock_name'] = ci['stock_name']
                    items['code_id'] = ci['stock_symbol'][2:]
                    items['prev_weight'] = ci['prev_weight']
                    items['target_weight'] = ci['target_weight']
                    items['change_status'] = items['target_weight'] - (
                    items['prev_weight'] if items['prev_weight'] != None else 0)
                    items['updated_at'] = ci['updated_at']
                    print(items, '--')
                    yield items
        if result_json['maxPage'] > 1:
            symbol = response.meta['zh_symbol']
            pages = arange(2, result_json['maxPage'] + 1)
            for i in pages:
                R = Request(url=self.url_model_page % (symbol, str(i)), meta={'cookiejar': 2, 'zh_symbol': symbol},
                            headers=self.api_headers, cookies=self.r_cookie, callback=self.api_zuhe_parse)
                yield R
