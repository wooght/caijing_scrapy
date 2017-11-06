# -*- coding: utf-8 -*-

#通过python脚本启动scrapy

from scrapy.cmdline import execute
import threading
from threading import Timer


#scrapy 运行接口
def scrapyrun(args):
    execute(["scrapy", "crawl", args])

spiders = ['news']
for item in spiders:
    scrapyrun(item)
