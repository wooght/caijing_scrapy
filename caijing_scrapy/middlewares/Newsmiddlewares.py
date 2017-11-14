# -*- coding: utf-8 -*-

# 下载中间件
# by wooght 2011-11
# 依赖.settings
# phantomjs 实现下载

from caijing_scrapy.middlewares.Wmiddlewares import Wdownloadmiddlewares as Dobj

import time
import random
import numpy as np
from scrapy.http import Request, FormRequest, HtmlResponse

class WooghtDownloadMiddleware(Dobj):
    #默认开启webdriver
    def __init__(self):
        self.set_cap()

    #执行下载操作,返回response
    def process_request(self, request, spider):
        js = "var q=document.body.scrollTop=2000"
        url=request.url;
        delay_time = random.randint(0,2)
        print('休息中....',delay_time)
        time.sleep(delay_time)                                               #随机休息时间
        try:
            self.open_url(url)
        except Exception as e:
            print('open_url deild',e)
            return None
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
                    print(button_class,'-=-=---===button click--====--=-=-=-=')
                    button_class.click()
        elif(spider.name=='news'):
            not_html = 'html' in url
            if(not not_html and 'yicai' in url):
                print('------------>yicai------>')
                arr_num = [1,2,3,4,5]
                for i in arr_num:
                    button_id = self.driver.find_element_by_id('divMore')        #多次点击更多按钮
                    time.sleep(2)
                    button_id.click()
            elif(url=="http://money.163.com/"):
                print('------------>mony163------>')
                # arr_num = np.arange(10)
                # for i in arr_num:
                #     time.sleep(2)
                #     js = 'clickLoadMore();'
                #     self.driver.execute_script(js)
            else:
                print('------------>sina,qq,web-->---------->')
        body = self.driver.page_source
        print(self.driver.title,'=-=-=-=-=---SUCCESS--给spider处理--=-=-=-=-=-')
        return HtmlResponse(body=body, encoding='utf-8',request=request,url=str(url))
