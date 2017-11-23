#encoding utf-8
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import model.Db as T
import providers.wfunc as wfunc
import matplotlib as mpl
import matplotlib.pyplot as plt     #matplotlib.pyplot 绘图主键
import seaborn as sns
import numpy as np
import pandas as pd
import time

mpl.rcParams['font.sans-serif'] = ['SimHei']    #指定默认字体 解决中文问题

try:
    code_id = sys.argv[1]               #股票代码
except:
    code_id = 1
pic_name = "\codes_"+str(code_id)+'_'+wfunc.today(strtime=False)+".png"
pic_path = "F:\homestead\caijing_lvl\public\pic_attitude_topic"+pic_name
start = int(time.time()-90*3600*24)
r = T.select([T.topic.c.cp_attitude,T.topic.c.put_time]).where(T.topic.c.code_id==code_id).where(T.topic.c.put_time>start)
s = T.conn.execute(r)
obj = []
for item in s.fetchall():
    datatime = time.strftime("%Y-%m-%d",time.localtime(int(item[1])))
    obj.append({'attitude':item[0],'datatime':datatime})

quotes = pd.DataFrame(obj)
quotes.index = quotes['datatime']   #将所有改为某列的值
quotes['attitude'] = pd.to_numeric(quotes['attitude'])
quotes['datatime'] = pd.to_datetime(quotes['datatime'])
attitudes = quotes['attitude'].groupby(quotes['datatime'])
attitudes_mean = attitudes.mean()
attitudes_mean = pd.DataFrame(attitudes_mean)

attitudes_mean['datatime'] = attitudes_mean.index
def quotes_ys(df,df2):
    sns.set(style="ticks",palette="muted",color_codes=True)
    plt.xlabel('datatime')
    plt.ylabel('shou')
    plt.title('topic语义分布',fontsize=16,color='red')
    plt.grid(True)                  #是否显示网格
    ax = sns.stripplot(x="datatime", y="attitude", data=df)
    # ax2 = sns.lmplot(x=df2['datatime'],y=df2['attitude'],data=df2)
    ax.tick_params(axis='x',labelsize=4)
    plt.savefig(pic_path)
    plt.show()
    print(pic_name)
quotes_ys(quotes.sort_index(axis=1,ascending=True),attitudes_mean)
