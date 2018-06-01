#encoding utf-8
# 行情展示
# by wooght
# 2017-11

import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import model.Db as T
import common.wfunc as wfunc
import matplotlib as mpl
import matplotlib.pyplot as plt     #matplotlib.pyplot 绘图主键
import seaborn as sns
import numpy as np
import pandas as pd
import json
import os
mpl.rcParams['font.sans-serif'] = ['SimHei']    #指定默认字体 解决中文问题

try:
    code_id = sys.argv[1]               #股票代码
except:
    code_id = 2
pic_name = "\codes_"+str(code_id)+'_'+wfunc.today(strtime=False)+".png"
pic_path = "F:\homestead\caijing_lvl\public\seaborn_pic"+pic_name

def sql(code_id):
    r = T.select([T.quotes_item.c.quotes,T.quotes_item.c.update_at]).where(T.quotes_item.c.code_id==code_id)
    s = T.conn.execute(r)
    item = s.fetchall()[0]
    return item
item = sql(code_id)
#更新判断 否则更新
if(str(item[1]) != wfunc.today(strtime=False)):
    os.chdir('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
    osrun = os.system("scrapy crawl quotes_item -a codeid="+str(code_id))
    item = sql(code_id)
print(item[0])
obj = json.loads(item[0])
# print(obj)
# quotes = pd.DataFrame(obj)
# quotes.index = quotes['datatime']   #将所有改为某列的值
# quotes['gao'] = pd.to_numeric(quotes['gao'])
# quotes['di'] = pd.to_numeric(quotes['di'])
# quotes['shou'] = pd.to_numeric(quotes['shou'])
# quotes['datatime'] = pd.to_datetime(quotes['datatime'])
# sns.set(style="darkgrid",palette="muted",color_codes=True)
# def quotes_ys(df):
#     sns.set(style="ticks",palette="muted",color_codes=True)
#     plt.xlabel('datatime')
#     plt.ylabel('shou')
#     plt.title('lmplot 线性行情',fontsize=16,color='red')
#     plt.grid(True)                  #是否显示网格
#     plt.plot(df.loc[:,['shou','gao','di']])
#     plt.legend()                    #图例
#     plt.savefig(pic_path)
#     plt.show()
#     print(pic_name)
# quotes_ys(quotes.sort_index(axis=1,ascending=True))
