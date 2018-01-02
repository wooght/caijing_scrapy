# -*- coding: utf-8 -*-
# ########################################
# concept 概念爬取中间件
# by wooght
# 2017-11
# ########################################

from scrapy.http import HtmlResponse

from caijing_scrapy.middlewares.Wmiddlewares import Wdownloadmiddlewares as Dobj
from common.werror import Werror


class WooghtDownloadMiddleware(Dobj):
    # 开启webdriver 设置phantomjs
    def __init__(self):
        self.stdout_utf8 = False
        self.timeout = 20
        self.set_cap()

    # 执行下载操作,返回response
    def process_request(self, request, spider):
        js = "var q=document.body.scrollTop=2000"
        url = request.url;
        self.delay()

        if ('phantomjs' not in request.meta.keys()):
            print('get agentmiddleware to run', request.url)
            return None
        # 尝试打开网页 无法打开则跳过 返回None
        try:
            self.open_url(url)
        except Werror as e:
            print('open_url deild', e)
        except ConnectionRefusedError:
            return None

        return HtmlResponse(body=body, encoding='utf-8', request=request, url=str(url))
