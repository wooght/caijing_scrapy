# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
#代理
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType

import time
import random
from scrapy.http import Request, FormRequest, HtmlResponse
import scrapy.settings

#headers
cap = webdriver.DesiredCapabilities.PHANTOMJS
useragentlist = [
                    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36 QIHU 360EE',
                    'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
                ]
refererlist = [
                'http://www.baidu.com',
                'http://www.qq.com',
                'https://zhidao.baidu.com/'
              ]
cap["phantomjs.page.settings.resourceTimeout"] = 10                             #请求超时时间
cap["phantomjs.page.settings.loadImages"] = False
cap["phantomjs.page.settings.disk-cache"] = False
cap["phantomjs.page.settings.accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
cap["phantomjs.page.customHeaders.Cookie"] = 'aliyungf_tc=AQAAAIplnShTMAQAebbT3lEVm4rc3txx; '
cap["phantomjs.page.settings.userAgent"] = random.choice(useragentlist)
cap['phantomjs.page.settings.connection'] = 'keep-alive'
cap["browserName"] = 'Chrome'
# cap['phantomjs.page.settings.host'] = random.choice(refererlist)


#定义在外部 防止多次实例phantomjs
global  driver
#service_args=['..'] 具备访问加密请求https的功能
driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'],executable_path="F:\homestead\scripy_wooght/phantomjs",desired_capabilities=cap)

class WooghtDownloadMiddleware(object):

    def process_request(self, request, spider):
        global driver
        js = "var q=document.body.scrollTop=2000"
        url=request.url;
        if(spider.name=='news'):
            self.open_url(url)
            time.sleep(random.randint(1,3))                                 #随机休息时间
            not_html = 'html' in url
            if(not not_html and 'yicai' in url):
                arr_num = [1,2,3,4,5]
                for i in arr_num:
                    button_id = driver.find_element_by_id('divMore')        #多次点击更多按钮
                    time.sleep(1)
                    button_id.click()
            elif(url=="https://xueqiu.com/"):
                arr_num = [1,2,3,4]
                for i in arr_num:
                    time.sleep(1)
                    js = "var a=document.body.scrollTop="+str(i*3000)
                    driver.execute_script(js)
                for i in arr_num:
                    time.sleep(1)
                    button_class = driver.find_element_by_class_name('home__timeline__more')
                    print(button_class.text(),'-=-=---===ddd--====--=-=-=-=')
                    button_class.click()
            body = driver.page_source
            print(driver.title,'=-=-=-=-=SUCCESS!-=-=-=-=-=-')
            return HtmlResponse(body=body, encoding='utf-8',request=request,url=str(url))


    #关闭浏览器
    def spider_closed(self, spider, reason):
        global driver
        print ('close driver......')
        driver.quit()

    def open_url(self,url):
        global driver
        global useragentlist
        #动态设置agent
        driver.desired_capabilities['phantomjs.page.settings.userAgent'] = random.choice(useragentlist)
        try:
            return driver.get(url)
        except:
            print('=--===--==!!!!Open Error!!!-=-=--=-=-=')
            time.sleep(1)
            proxy=webdriver.Proxy()
            proxy.proxy_type=ProxyType.MANUAL
            proxy.http_proxy=random.choice(settings['HTTP_IPS'])
            # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
            proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
            driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
