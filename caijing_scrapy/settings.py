# -*- coding: utf-8 -*-

# Scrapy settings for caijing_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'caijing_scrapy'

SPIDER_MODULES = ['caijing_scrapy.spiders']
NEWSPIDER_MODULE = 'caijing_scrapy.spiders'
BOT_PATH = 'F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy'
PHANTOMJSPATH='F:\homestead\scripy_wooght/phantomjs'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#要注意版本问题 版本太旧 读出来的JS内容不一样
#默认user-agent
USER_AGENT = [
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36 QIHU 360EE',
                'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
             ]

HEADERS={
    'Referer':'http://www.baidu.com',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded"
    }

PHANTOMJSPAGES={
    "phantomjs.page.settings.resourceTimeout" : 200,                              #资源请求超时时间 单位ms
    "phantomjs.page.settings.loadImages" : False,                                 #不加载图片
    "phantomjs.page.settings.disk-cache" : False,                                 #启用缓存
    "phantomjs.page.settings.accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "phantomjs.page.customHeaders.Cookie" : 'aliyungf_tc=AQAAAIplnShTMAQAebbT3lEVm4rc3txx;',
    'phantomjs.page.settings.connection' : 'keep-alive',
    "browserName" : 'Chrome',
}

# Obey robots.txt rules
# 是否遵循robots协议
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)

#整个系统并发量
CONCURRENT_REQUESTS = 32
#同个域 并发量
CONCURRENT_REQUESTS_PER_DOMAIN = 4
#同个IP 并发量
CONCURRENT_REQUESTS_PER_IP = 4

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1                                  #同一网站延迟时间
RANDOMIZE_DOWNLOAD_DELAY = True                     #随机等待时间 在download-delay的基础上

DNS_TIMEOUT = 10                                    #DNS解析等等最大时间
DOWNLOAD_TIMEOUT = 5                                #等待/超时的最大时间 S

# HTTPERROR_ALLOWED_CODES= [521]                      #可继续执行的访问错误

RETRY_ENABLED = True
RETRY_TIMES = 1                                     #重试一次即可放弃

LOG_ENABLED = True                                   #日志
LOG_LEVEL = 'WARNING'                                  #运行日志级别 DEBUG,INFO,WARNING,ERROR,CRITICAL,SILENT

LOGSTATS_INTERVAL = 60                              #打印item处理数据

TELNETCONSOLE_ENABLED = True
# TELNETCONSOLE_PORT = '50853'                          #监控端口

#IP池
HTTP_IPS = [
    '61.152.230.26:8080',
    '211.103.208.244:80',
    '115.219.251.236:9999',
    '61.158.111.142:53281',
    '118.31.103.7:3128'
]

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# Request 请求默认 HEADERS
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'caijing_scrapy.middlewares.CaijingScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': 543,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'caijing_scrapy.pipelines.pipelines.CaijingScrapyPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
