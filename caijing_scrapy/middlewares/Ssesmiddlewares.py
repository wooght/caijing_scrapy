# -*- coding: utf-8 -*-

# 上海证券公告爬取 下载中间件
# by wooght 2017-11

import time

import numpy as np
from scrapy.http import HtmlResponse

import caijing_scrapy.providers.wfunc as wfunc
from caijing_scrapy.middlewares.Wmiddlewares import Wdownloadmiddlewares as Dobj


class WooghtDownloadMiddleware(Dobj):

    # 主函数
    # 执行下载操作,返回response
    def process_request(self, request, spider):
        self.body = ''
        self.url = request.url
        self.set_cap()
        self.open_url(self.url)  # 打开地址
        self.set_data()  # 输入日期
        self.click_more()  # 点击更多N次
        # body = self.driver.find_element_by_id('ul_his_fulltext').get_attribute('innerHTML') 这里得到的ID和实际ID不同  ????????
        print(self.driver.title, '=-=-=-=-=---SUCCESS--给spider处理--=-=-=-=-=-')
        return HtmlResponse(body=self.body, encoding='utf-8', request=request, url=str(self.url))

    # 点击下一页
    def click_more(self):
        self.body += self.driver.page_source
        arr = np.arange(50)
        for i in arr:
            try:
                more_button = self.driver.find_element_by_xpath(
                    "//ul[@class='pagination']/li[last()]/a")  # 通过位置筛选时,一定要层层去找
                print(more_button.get_attribute('innerHTML'), '-=-=-=-=-=-=-=-')
                more_button.click()  # 每次页面加载后,都要重新获取焦点
                print('next_button click..', i)
                self.driver.save_screenshot('errpic/' + str(i) + '.png')
            except Exception as e:
                print('is last one:', i, '----error:', e)
            time.sleep(3)
            self.body += self.driver.find_element_by_class_name('modal_pdf_list').get_attribute('innerHTML')

    # 填写日期
    def set_data(self):
        time.sleep(2)
        data_input = self.driver.find_element_by_id('start_date')  # 找到输入框
        readonlyjs = "var readonlyjs = document.getElementById('start_date');readonlyjs.removeAttribute('readOnly');"
        self.driver.execute_script(readonlyjs)
        data_input.clear()  # 清空内容
        data_input.send_keys(self.get_data())  # 写入内容
        time.sleep(2)
        data_input = self.driver.find_element_by_id('end_date')  # 找到输入框
        readonlyjs = "var readonlyjs = document.getElementById('end_date');readonlyjs.removeAttribute('readOnly');"
        self.driver.execute_script(readonlyjs)
        data_input.clear()  # 清空内容
        data_input.send_keys(wfunc.today())  # 写入内容
        time.sleep(2)
        search_button = self.driver.find_element_by_id('btnQuery')
        search_button.click()
        self.driver.switch_to_window(self.driver.window_handles[0])  # 窗口切换
        time.sleep(4)
        self.driver.save_screenshot('errpic/ssn.png')

    # 时间生产
    def get_data(self):
        start_time = int(time.time()) - 20 * 3600 * 24
        start_data = time.strftime("%Y-%m-%d", time.localtime(start_time))
        return start_data
