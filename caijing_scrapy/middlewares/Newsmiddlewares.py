# -*- coding: utf-8 -*-

# 新闻下载中间件
# by wooght 2011-11
# 依赖.settings

from caijing_scrapy.middlewares.Wmiddlewares import Wdownloadmiddlewares as Dobj

import time
import random
import numpy as np
from scrapy.http import Request, FormRequest, HtmlResponse
from caijing_scrapy.providers.werror import Werror

class WooghtDownloadMiddleware(Dobj):
    #开启webdriver 设置phantomjs
    def __init__(self):
        self.stdout_utf8=False
        self.timeout = 20
        self.set_cap()

    #执行下载操作,返回response
    def process_request(self, request, spider):
        js = "var q=document.body.scrollTop=2000"
        url=request.url;
        self.delay()

        #返回None  将交由下一个middle操作
        #返回request 将从新构建请求
        #返回response 返回给spider的paser操作,跳过后面的downloadermiddlewares
        if('phantomjs' not in request.meta.keys()):
            print('get agentmiddleware to run',request.url)
            return None
        #尝试打开网页 无法打开则跳过 返回None
        try:
            self.open_url(url)
        except Werror as e:
            print('open_url deild',e)
        except ConnectionRefusedError:
            return None

        #雪球头条
        if(spider.name=='topics'):
            print('------------>xueqiu------>')
            if(url=="https://xueqiu.com"):
                arr_num = np.arange(10)
                for i in arr_num:
                    time.sleep(1)
                    js = "var a=document.body.scrollTop="+str(i*3000)+";"
                    self.driver.execute_script(js)
                for i in arr_num:
                    time.sleep(2)
                    button_class = self.driver.find_element_by_class_name('home__timeline__more')
                    print('-=-=---===button click--====--=-=-=-=')
                    button_class.click()
        #新闻
        elif(spider.name=='news'):
            not_html = 'html' in url
            if(not not_html and 'yicai' in url):
                print('------------>yicai------>')
                arr_num = [1,2,3,4,5]
                for i in arr_num:
                    button_id = self.driver.find_element_by_id('divMore')        #多次点击更多按钮
                    time.sleep(2)
                    button_id.click()
            elif("money.163.com" in url):
                print('------------>mony163------>')
                arr_num = np.arange(10)
                for i in arr_num:
                    time.sleep(2)
                    # js = 'var a = clickLoadMore();'
                    # self.driver.execute_script(js)
                    try:
                        load_more_btn = self.driver.find_element_by_class_name('load_more_btn')
                        load_more_btn.click()
                    except Exception as e:
                        print('no more..')
                        break
            else:
                print('------------>sina,qq-->---------->')
        body = self.driver.page_source
        print(self.driver.title+'SUCCESS--To spider')
        # print(self.driver.window_handles)                   #打印当前所有窗口
        return HtmlResponse(body=body, encoding='utf-8',request=request,url=str(url))
