# -*- coding: utf-8 -*-

# 巨潮资讯网 公告抓取 下载中间件
# by wooght 2017-11
# 依赖 .settings numpy
# phantomjs 实现下载

from caijing_scrapy.middlewares.Wmiddlewares import Wdownloadmiddlewares as Dobj

import time
import random
from scrapy.http import Request, FormRequest, HtmlResponse
import caijing_scrapy.providers.wfunc as wfunc

import numpy as np
import re

class WooghtDownloadMiddleware(Dobj):

    #主函数
    #执行下载操作,返回response
    def process_request(self, request, spider):
        self.body=''
        self.url=request.url;
        self.set_cap()
        self.open_url(self.url)             #打开地址
        self.set_data()                     #输入日期
        time.sleep(5)
        self.click_more()                   #点击更多N次
        # body = self.driver.find_element_by_id('ul_his_fulltext').get_attribute('innerHTML') 这里得到的ID和实际ID不同  ????????
        print(self.driver.title,'=-=-=-=-=---SUCCESS--给spider处理--=-=-=-=-=-')
        return HtmlResponse(body=self.driver.page_source, encoding='utf-8',request=request,url=str(self.url))

    #点击加载更多
    def click_more(self):
        arr = np.arange(1000)
        for i in arr:
            print(i)
            time.sleep(2)
            try:
                more_button = self.driver.find_element_by_xpath('//div[@class="show-more"]')
                more_button.click()                                         #每次页面加载后,都要重新获取焦点
            except:
                self.driver.execute_script('addMore();')
            js = "var a=document.body.scrollTop="+str(i*2000)+";"
            self.driver.execute_script(js)
            self.driver.implicitly_wait(10)                             #隐式等待页面加载

    #填写日期
    def set_data(self):
        data_input = self.driver.find_element_by_id('rangeA')           #找到输入框
        data_input.clear()                                              #清空内容
        data_input.send_keys(self.get_data())                           #写入内容

        search_button = self.driver.find_element_by_class_name('com-search-btn')
        search_button.click()
        self.driver.switch_to_window(self.driver.window_handles[0])     #窗口切换

    #时间生产
    def get_data(self):
        today = time.strftime("%Y-%m-%d",time.localtime())
        start_time  = int(time.time())-10*3600*24
        start_data = time.strftime("%Y-%m-%d",time.localtime(start_time))
        return start_data+" ~ "+today
