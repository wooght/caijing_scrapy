# -*- coding: utf-8 -*-
# ##################################
# 行情数据组装
# by wooght
# 2017-11
# ##################################
import json
import os
import sys

sys_path = os.path.dirname(__file__)+'/../../'
sys.path.append(sys_path)
from factory.basedata import basedata
import common.wfunc as wfunc

# 获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 600519


class quotes_data(basedata):
    def get_quotes(self):
        quotes = self.select_quotes(code_id, getpd=False)
        if (str(quotes[1]) != wfunc.today(strtime=False)):
            os.chdir(sys_path)
            osrun = os.system("scrapy crawl quotes_item -a codeid=" + str(code_id))
            quotes = self.select_quotes(code_id, getpd=False)
        obj = json.loads(quotes[0])
        # 顺序排列
        obj = sorted(obj, key=lambda d: d['datatime'], reverse=False)
        result = ''
        for i in obj:
            result += '["' + i['datatime'] + '","' + i['kai'] + '","' + i['shou'] + '","' + i['di'] + '","' + i[
                'gao'] + '","' + i['liang'] + '"],'
        return "[" + result + "]"


a = quotes_data()
b = a.get_quotes()
print(b)
