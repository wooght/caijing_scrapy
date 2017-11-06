# -*- coding: utf-8 -*-

# 扩展函数
# by wooght 2017-11

import time
import re
#字符串时间转换为时间暨
def time_num(str,format):
    timeArray = time.strptime(str, format)
    timestamp = time.mktime(timeArray)
    return int(timestamp)

def today():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) #格式化时间 2017-10-23 17:10:54

#雪球时间匹配
def search_time(str):
    str_search=re.search(r'\D*(\d{4}-\d{2}-\d{2} .*)',str)
    if(str_search):
        return str_search.group(1)
    else:
        str_search = re.search(r'\D*(\d{2}-\d{2} .*)',str)
        if(str_search):
            year = time.strftime("%Y")
            str = year+'-'+str_search.group(1)
            return str
        else:
            return today()
