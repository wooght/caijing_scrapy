# -*- coding: utf-8 -*-

# 网易财经行业板块 下载中间件
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
        if(spider.name=='plates'):
            self.get_plateid()
        else:
            self.find_plate(request.meta['plates'])
        print(self.driver.title,'=-=-=-=-=---SUCCESS--给spider处理--=-=-=-=-=-')
        return HtmlResponse(body=self.body, encoding='utf-8',request=request,url=str(self.url))

    #获取行业ID
    def get_plateid(self):
        self.body = self.driver.find_element_by_id('f0-f7').get_attribute('innerHTML')

    #查找地域位置按钮
    def find_plate(self,plates):
        for num in plates:
            if(len(num)<5):
                num='0'+num
            try:
                url_str = "javascript:page.components.clickNavTreeNodeByHash(\'#query=hy0%s&DataType=HS_RANK&sort=PERCENT&order=desc&count=24&page=0\');"%(num)
                # region_bt = self.driver.find_element_by_xpath('//div[@class="bread-crumbs-details"]/a[%s]'%(num))
                # region_bt.click()
                # 这里的按钮是js运行,点击按钮及运行相应的JS  可以直接运行JS
                self.driver.execute_script(url_str)
                time.sleep(3)
                print('访问------',num,'------板块')
                self.test=0
                self.get_tr(num)
            except Exception as e:
                print(url_str,'查找失败!!!')
                print(e)

    #读取每一行数据 并且翻页拼接
    def get_tr(self,num):
        #在webdriver中 find_element_by_xpath只返回一个webelement对象 不会返回列表  默认是第一个对象 find_elements_by_xpath会返回列表
        totletd = self.driver.find_element_by_xpath('//table[@class="ID_table stocks-info-table"]/tbody/tr[last()]/td')
        totle=totletd.text
        totle_num = int(totle)
        #每一页最多24条 但网页的ID不是从0开始
        while totle_num>24:
            totle_num-=24
        for i in np.arange(totle_num):
            try:
                xpathstr = '//table[@class="ID_table stocks-info-table"]/tbody/tr['+str(i+1)+']'
            except Exception as e:
                print('----------------------------------------->读取tr行出错--------->',e.args)
                continue
            try:
                tr=self.driver.find_element_by_xpath(xpathstr)
                #innerhtml不能获取tbody的内容 故这里跳过tbody来进行拼接
                #get_attribute 读取某个属性 如 href
                add_tr = '<tr><td>'+str(num)+'</td>'+str(tr.get_attribute("innerHTML"))+'</tr>'
                self.body+=add_tr
            except Exception as e:
                print(xpathstr,e.args,'当前I值为:',i+1,'-->url:',self.url)
        #页面读取完后,进入下一页 或者下一个地域
        try:
            next_button = self.driver.find_element_by_xpath('//div[@class="ID_pages mod-pages"]//a[last()]')
            strr = next_button.text
            if(strr=="下一页"):
                next_button.click()
                time.sleep(2)
                self.get_tr(num)
            else:
                return True
        except Exception as e:
            print(e.args,':Error')
