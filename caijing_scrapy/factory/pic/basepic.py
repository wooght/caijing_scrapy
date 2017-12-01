#encoding utf-8
#
# 生成分析图片基础模块
# by wooght
# 2017-11
#
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import model.Db as T
import providers.wfunc as wfunc
import matplotlib as mpl
import matplotlib.pyplot as plt     #matplotlib.pyplot 绘图主键
import seaborn as sns
import numpy as np
import pandas as pd
import json

class Basepic(object):
    pic_path = 'F:\homestead\caijing_lvl\public'
    def __init__(self):
        self.mpl = mpl
        self.mpl.rcParams['font.sans-serif'] = ['SimHei']    #指定默认字体 解决中文问题
        self.plt = plt
        self.sns = sns
        self.np = np
        self.pd = pd
    #行情数据查询
    def select_quotes(self,id):
        #行情查询
        r = T.select([T.quotes_item.c.quotes]).where(T.quotes_item.c.code_id==id)
        s = T.conn.execute(r)
        #json接卸
        for item in s.fetchall():
            obj = json.loads(item[0])
        quotes = self.pd.DataFrame(obj)
        quotes['gao'] = self.pd.to_numeric(quotes['gao'])
        quotes['di'] = self.pd.to_numeric(quotes['di'])
        quotes['shou'] = self.pd.to_numeric(quotes['shou'])
        quotes['zd_range'] = self.pd.to_numeric(quotes['zd_range'])
        return quotes
