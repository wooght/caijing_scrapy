#encoding utf-8
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import Db as T
import providers.wfunc as wfunc
import matplotlib as mpl
import matplotlib.pyplot as plt     #matplotlib.pyplot 绘图主键
import seaborn as sns
import numpy as np
import pandas as pd
import json

try:
    code_id = sys.argv[1]               #股票代码
except:
    code_id = 1
pic_name = "\codes_"+str(code_id)+'_'+wfunc.today(strtime=False)+".png"
pic_path = "F:\homestead\caijing_lvl\public\seaborn_pic"+pic_name

r = T.select([T.quotes_item.c.quotes]).where(T.quotes_item.c.code_id==code_id)
s = T.conn.execute(r)
for item in s.fetchall():
    obj = json.loads(item[0])

quotes = pd.DataFrame(obj)
quotes.index = quotes['datatime']   #将所有改为某列的值
# quotes = quotes.convert_objects(convert_numeric=True)   #小数有可能是obj类型 要运算就必须类型转换
quotes['gao'] = pd.to_numeric(quotes['gao'])
quotes['di'] = pd.to_numeric(quotes['di'])
quotes['shou'] = pd.to_numeric(quotes['shou'])
quotes['datatime'] = pd.to_datetime(quotes['datatime'])
sns.set(style="darkgrid",palette="muted",color_codes=True)
def quotes_ys(df):
    sns.set(style="ticks",palette="muted",color_codes=True)
    plt.xlabel('datatime')
    plt.ylabel('shou')
    plt.title('quotes lmplot',fontsize=16,color='red')
    plt.grid(True)                  #是否显示网格
    plt.plot(df.loc[:,['shou','gao','di']])
    plt.legend()                    #图例
    plt.savefig(pic_path)
    plt.show()
    print(pic_name)
quotes_ys(quotes.sort_index(axis=1,ascending=True))
