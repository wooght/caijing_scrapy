# -*- coding: utf-8 -*-
#
# 上海证券公告抓取
# by wooght 2017-11
#
import scrapy
from caijing_scrapy.items import NoticesItem


class SseinfoSpider(scrapy.Spider):
    name = 'sseinfo'
    allowed_domains = ['sse']
    start_urls = ['http://www.sse.com.cn/disclosure/listedinfo/announcement/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,           #处理普通静态页面
           'caijing_scrapy.middlewares.Ssesmiddlewares.WooghtDownloadMiddleware': 543,
        },
        'LOG_LEVEL':'WARNING'
    }

    def parse(self, response):
        item = NoticesItem()
        all = response.xpath('//dd[@class="just_this_only"]')
        for dd in all:
            item['code_id'] = dd.xpath("@data-seecode").extract_first()
            item['title'] = dd.xpath("a[1]/@title").extract_first()
            item['datatime'] = dd.xpath("@data-time").extract_first()
            print(item)
            yield item


# <dd data-time="2017-11-16" data-seecode="600004" data-method="fn_bulletin" class="just_this_only">
# <span>2017-11-16</span>
# <em data-toggle="modal" data-target=".bs-pdf-modal-lg" class="pdf-first"><a href="http://static.sse.com.cn/disclosure/listedinfo/announcement/c/2017-11-16/600004_20171116_1.pdf" title="白云机场2017年第一次临时股东大会会议资料" target="_blank">600004:白云机场2017年第一次临时股东大会会议资料</a></em>
# <a href="http://static.sse.com.cn/disclosure/listedinfo/announcement/c/2017-11-16/600004_20171116_1.pdf" target="_blank" title="白云机场2017年第一次临时股东大会会议资料" class="hidden-xs">
# <i><img src="/images/ui/pdf-ico.jpg"></i>
# </a>
# </dd>
