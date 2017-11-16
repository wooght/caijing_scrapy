# -*- coding: utf-8 -*-

#通过python脚本启动scrapy
import sys
from scrapy.cmdline import execute
execute(["scrapy", "crawl", sys.argv[1]])
