# -*- coding: utf-8 -*-

#
# 带webdriver功能下载中间件起始类
# by wooght 2017-11
#

import sys,io
import selenium
from selenium import webdriver
import time
import random
from scrapy.http import Request, FormRequest, HtmlResponse
from caijing_scrapy.settings import USER_AGENT,PHANTOMJSPAGES,PHANTOMJSPATH
import caijing_scrapy.providers.wfunc as wfunc
from caijing_scrapy.providers.werror import Werror
# #代理
# from selenium.webdriver.common.proxy import Proxy
# from selenium.webdriver.common.proxy import ProxyType

class Wdownloadmiddlewares(object):

    save_error_pic = True       #保存错误页面图片
    random_agent = False        #随机agent
    disk_cache = False          #启用浏览器缓存
    stdout_utf8 = False         #输出缓冲编码
    timeout = 10                #加载超时时间


    # 创建webdriver
    # 设置driver属性
    def set_cap(self):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        refererlist = [
                        'http://www.baidu.com','http://www.qq.com','https://zhidao.baidu.com/'
                      ]
        for key,value in PHANTOMJSPAGES.items():
            cap[key] = value
        cap['phantomjs.page.settings.userAgent'] = random.choice(USER_AGENT)
        if(self.disk_cache):
            cap['phantomjs.page.settings.disk-cache'] = True
        if(self.stdout_utf8):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
        wfunc.e(cap)

        #创建webdriver
        # #service_args中:--ssl-protocol=any具备访问加密请求https的功能
        self.driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'],executable_path=PHANTOMJSPATH,desired_capabilities=cap)
        self.driver.maximize_window()                       #设置全屏
        self.driver.set_page_load_timeout(self.timeout)      #设置超时时间

        self.driver.set_script_timeout(self.timeout*2)         #设置异步超时时间
        # self.driver.implicitly_wait(5)                    #设置只能等待时间

        wfunc.e('!+!+=new driver run=+!+!')

    #爬虫执行完后 余下操作
    def spider_closed(self, spider, reason):
        wfunc.e('driver closed')
        self.driver.quit()                          #关闭浏览器

    #访问连接,浏览器解析连接response
    def open_url(self,url):
        #动态设置agent
        if(self.random_agent):
            self.driver.desired_capabilities['phantomjs.page.settings.userAgent'] = random.choice(USER_AGENT)
        try:
            wfunc.e(wfunc.today()+'open url:'+url)
            t_one = time.time()
            self.driver.get(url)
            t_two = time.time()
            wfunc.e('spend times:'+str(t_two-t_one))
        except selenium.common.exceptions.TimeoutException as e:
            wfunc.e("Timeout")
            if(self.save_error_pic):
                self.driver.save_screenshot('errpic/'+str(int(time.time()))+".png") #保存报错图片
            raise Werror('...Timeout....')
        except Exception as e:
            wfunc.e_error(e)
            self.driver.quit()                                                      #退出旧的driver,减小内存
            self.set_cap()                                                          #10061错误,及phantomjs内容溢出,需重新启动
            raise ConnectionRefusedError()
            # self.set_proxy()

    #IP代理
    def set_proxy(self):
        proxy=webdriver.Proxy()
        proxy.proxy_type=ProxyType.MANUAL
        proxy.http_proxy=random.choice(HTTP_IPS)
        # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
        proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)

    #随机等待时间
    def delay(self):
        delay_time = random.randint(0,2)
        wfunc.e('delayd....'+str(delay_time))
        time.sleep(delay_time)
