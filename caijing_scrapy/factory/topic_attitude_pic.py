#encoding utf-8
#
# topic语义分析图
# company_attitude
# Plate_Attitude
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
import time
import json

mpl.rcParams['font.sans-serif'] = ['SimHei']    #指定默认字体 解决中文问题
#获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 600519

#查询plate_id
ps = T.select([T.listed_company.c.plate_id]).where(T.listed_company.c.codeid==code_id)
pr = T.conn.execute(ps)
plate_id = pr.fetchall()[0][0]

class topic_attitude_pic():

    def __init__(self,code_id,plate_id):
        self.code_id = code_id
        self.plate_id = plate_id
        #图片路径及名称
        self.now_day = wfunc.today(strtime=False)
        pic_name = "F:\homestead\caijing_lvl\public\pic_attitude_topic\codes_"+str(code_id)+'_'+self.now_day
        self.pic_path = pic_name+".png"
        self.strip_pic_path = pic_name+"strip.png"
        #查询开始时间
        self.start = int(time.time()-90*3600*24)

    #attitude数据组装施工
    def select_atd(self,*args,**kargs):
        result = T.conn.execute(args[0])
        new_list = []
        for item in result.fetchall():
            obj = {};n=1
            put_time = time.strftime("%Y-%m-%d",time.localtime(int(item[0])))
            obj['time'] = put_time
            for i in kargs['columns']:
                obj[i] = item[n]
                n+=1
            new_list.append(obj)
        new_pd = pd.DataFrame(data=new_list)
        #查询为空 返回模拟数据
        if(len(new_pd)<1):
            new_pd['time'] = pd.Series([1,2,3,4,5])
            for item in kargs['columns']:
                new_pd[item] = 0.01
            return new_pd
        new_pd['time'] = pd.to_datetime(new_pd['time'])
        for item in kargs['columns']:
            new_pd[item] = pd.to_numeric(new_pd[item])
        new_pd.index = new_pd['time']
        return new_pd

    #company_attitude 数据组装车间
    def select_cp_atd(self):
        #文章cp_attitude查询
        s = T.select([T.topic.c.put_time,T.topic.c.cp_attitude]).where(T.topic.c.code_id==self.code_id).where(T.topic.c.put_time>self.start)
        pddata = self.select_atd(s,columns = ['cp_attitude'])
        return pddata

    #plate_attitude 数据组装车间
    def select_plate_atd(self):
        #文章plate_attitude查询
        s = T.select([T.topic.c.put_time,T.topic.c.plate_attitude]).where(T.topic.c.plate_id==self.plate_id).where(T.topic.c.put_time>self.start)
        try:
            pddata = self.select_atd(s,columns = ['plate_attitude'])
        except:
            print(self.plate_id)
        return pddata

    #行情数据查询
    def select_quotes(self):
        #行情查询
        r = T.select([T.quotes_item.c.quotes]).where(T.quotes_item.c.code_id==self.code_id)
        s = T.conn.execute(r)
        #json接卸
        for item in s.fetchall():
            obj = json.loads(item[0])
        quotes = pd.DataFrame(obj)
        quotes.index = quotes['datatime']
        return quotes

    #数据分组求平均
    def atd_mean(self,pandas,attitude,time):
        #分组
        attitudes = pandas[attitude].groupby(pandas[time])
        #在分组的基础上求平均数
        attitudes_mean = attitudes.mean()
        attitudes_mean = pd.DataFrame(attitudes_mean)
        attitudes_mean[time] = pd.to_datetime(attitudes_mean.index)
        return attitudes_mean

    #分析数据组装
    def last_pandas(self,quotes,cp_atd,plate_atd):
        quotes['gao'] = pd.to_numeric(quotes['gao'])
        quotes['di'] = pd.to_numeric(quotes['di'])
        quotes['shou'] = pd.to_numeric(quotes['shou'])
        quotes['zd_range'] = pd.to_numeric(quotes['zd_range'])
        quotes['datatime'] = pd.to_datetime(quotes['datatime'])
        quotes['attitude']=''
        quotes['plate_attitude'] = ''
        cp_atd = self.atd_mean(cp_atd,'cp_attitude','time')
        plate_atd = self.atd_mean(plate_atd,'plate_attitude','time')
        for hang in quotes.index:
            if hang in cp_atd.index:
                quotes.loc[hang,['attitude']] = cp_atd.loc[hang,['cp_attitude']][0]
            else:
                quotes.loc[hang,['attitude']]=0
            if hang in plate_atd.index:
                quotes.loc[hang,['plate_attitude']] = plate_atd.loc[hang,['plate_attitude']][0]
            else:
                quotes.loc[hang,['plate_attitude']]=0
        #划定0.5语义中性线
        quotes.loc[:,'zero'] = 0.6
        return quotes
    #数据生成工厂
    def buide_datas(self):
        cp_atd = self.select_cp_atd()
        plate_atd = self.select_plate_atd()
        quotes = self.select_quotes()
        last_pandas = self.last_pandas(quotes,cp_atd,plate_atd)
        return last_pandas,cp_atd
    #运行接口
    def run(self):
        df,df2 = self.buide_datas()
        df = df.sort_index(axis=1,ascending=True)
        sns.set(style="ticks",palette="muted",color_codes=True)
        plt.xlabel('datatime')
        plt.ylabel('shou')
        plt.title('Topic Attitude',fontsize=16,color='red')
        plt.grid(True)                  #是否显示网格
        #绘制 情感平均图/涨跌幅对比图
        plt.plot(df.loc[:,['zd_range','attitude','zero']])
        plt.savefig(self.pic_path)
        plt.show()
        #绘制 情感分布散点图
        ax = sns.stripplot(x="time", y="cp_attitude", data=df2)
        ax.tick_params(axis='x',labelsize=4)
        plt.savefig(self.strip_pic_path)
        plt.show()
        #绘制行业情感平均图
        plt.title('Topic Plate_Attitude',fontsize=16,color='red')
        plt.plot(df.loc[:,['zd_range','plate_attitude','zero']])
        plt.show()
        print(self.now_day)

this = topic_attitude_pic(code_id,plate_id)
this.run()
