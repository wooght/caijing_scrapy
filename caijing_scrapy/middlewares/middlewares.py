# -*- coding: utf-8 -*-

# 下载中间件
# by wooght 2011-11
# 依赖.settings
# phantomjs 实现下载

from selenium import webdriver
#代理
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType

import time
import random
from scrapy.http import Request, FormRequest, HtmlResponse
from caijing_scrapy.settings import HTTP_IPS
from caijing_scrapy.settings import USER_AGENT
import caijing_scrapy.providers.wfunc as wfunc

import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码


class WooghtDownloadMiddleware(object):
    def __init__(self):
        self.set_cap()
        # self.set_proxy()

    #创建webdriver
    def set_cap(self):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        refererlist = [
                        'http://www.baidu.com','http://www.qq.com','https://zhidao.baidu.com/'
                      ]
        cap["phantomjs.page.settings.resourceTimeout"] = 2000                             #请求超时时间 单位ms
        cap["phantomjs.page.settings.loadImages"] = False
        cap["phantomjs.page.settings.disk-cache"] = True
        cap["phantomjs.page.settings.accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        cap["phantomjs.page.customHeaders.Cookie"] = 'aliyungf_tc=AQAAAIplnShTMAQAebbT3lEVm4rc3txx; '
        cap["phantomjs.page.settings.userAgent"] = random.choice(USER_AGENT)
        cap['phantomjs.page.settings.connection'] = 'keep-alive'
        cap["browserName"] = 'Chrome'

        #创建webdriver
        # #service_args=['..'] 具备访问加密请求https的功能
        # driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'],executable_path="F:\homestead\scripy_wooght/phantomjs",desired_capabilities=cap)
        self.driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'],executable_path="F:\homestead\scripy_wooght/phantomjs",desired_capabilities=cap)
        self.driver.implicitly_wait(10)        ##设置超时时间
        self.driver.set_page_load_timeout(10)  ##设置超时时间 两则同时设置才有效
        print('-----------------------------=>driver启动')
        self.driver.onResourceTimeout = self.function()
    def function(self):
        print('timeout')
    #执行下载操作,返回response
    def process_request(self, request, spider):
        js = "var q=document.body.scrollTop=2000"
        url=request.url;
        if(spider.name=='news'):
            delay_time = random.randint(0,2)
            print('休息中....',delay_time)
            time.sleep(delay_time)                                               #随机休息时间
            self.open_url(url)
            not_html = 'html' in url
            if(not not_html and 'yicai' in url):
                print('------------>yicai------>')
                arr_num = [1,2,3,4,5]
                for i in arr_num:
                    button_id = self.driver.find_element_by_id('divMore')        #多次点击更多按钮
                    time.sleep(2)
                    button_id.click()
            elif(url=="https://xueqiu.com"):
                print('------------>xueqiu------>')
                arr_num = [1,2,3,4]
                for i in arr_num:
                    time.sleep(1)
                    js = "var a=document.body.scrollTop="+str(i*3000)
                    self.driver.execute_script(js)
                for i in arr_num:
                    time.sleep(2)
                    button_class = self.driver.find_element_by_class_name('home__timeline__more')
                    print(button_class,'-=-=---===button click--====--=-=-=-=')
                    button_class.click()
            else:
                print('------------>sina,qq---------->')
            body = self.driver.page_source
            print(self.driver.title,'=-=-=-=-=---SUCCESS--给spider处理--=-=-=-=-=-')
            # self.driver.close()                                                     #关闭当前网页
            return HtmlResponse(body=body, encoding='utf-8',request=request,url=str(url))


    #关闭浏览器
    def spider_closed(self, spider, reason):
        print ('close driver......')
        self.driver.quit()                  #关闭浏览器
    #执行下载
    def open_url(self,url):
        #动态设置agent
        self.driver.desired_capabilities['phantomjs.page.settings.userAgent'] = random.choice(USER_AGENT)
        try:
            print(wfunc.today(),'open url......:',url,'......')
            t_one = time.time()
            self.driver.get(url)
            t_two = time.time()
            print('out time:',t_two-t_one)
        except Exception as e:
            print('=--===--==!!!! Open Url Error !!!-=-=--=-=-=',e)
            self.driver.quit()                                                      #退出旧的driver,减小内存
            time.sleep(1)
            self.set_cap()                                                          #10061错误,及phantomjs内容溢出,需重新启动
            # self.set_proxy()

    #IP代理
    def set_proxy(self):
        proxy=webdriver.Proxy()
        proxy.proxy_type=ProxyType.MANUAL
        proxy.http_proxy=random.choice(HTTP_IPS)
        # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
        proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
