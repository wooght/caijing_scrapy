# encoding utf-8
# ##################################
# 数据结构组装 基础模块
# by wooght
# 2017-11
# ##################################

from model import T
import numpy as np
import pandas as pd
import json,time

class  basedata():
    def __init__(self):
        self.np = np
        self.pd = pd

    #行情数据查询
    def select_quotes(self,id,getpd = True):
        #行情查询
        if(not getpd):
            r = T.select([T.quotes_item.c.quotes,T.quotes_item.c.update_at]).where(T.quotes_item.c.code_id==id)
            s = T.conn.execute(r)
            return s.fetchall()[0]
        r = T.select([T.quotes_item.c.quotes]).where(T.quotes_item.c.code_id==id)
        s = T.conn.execute(r)
        #json解析
        for item in s.fetchall():
            obj = json.loads(item[0])
        quotes = self.pd.DataFrame(obj)
        quotes['gao'] = self.pd.to_numeric(quotes['gao'])
        quotes['di'] = self.pd.to_numeric(quotes['di'])
        quotes['shou'] = self.pd.to_numeric(quotes['shou'])
        quotes['zd_range'] = self.pd.to_numeric(quotes['zd_range'])
        return quotes
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
        new_pd = self.pd.DataFrame(data=new_list)
        #查询为空 返回模拟数据
        if(len(new_pd)<1):
            new_pd['time'] = self.pd.Series([1,2,3,4,5])
            for item in kargs['columns']:
                new_pd[item] = 0.01
            return new_pd
        new_pd['time'] = self.pd.to_datetime(new_pd['time'])
        for item in kargs['columns']:
            new_pd[item] = self.pd.to_numeric(new_pd[item])
        return new_pd

    #数据分组求平均
    def atd_mean(self,pandas,attitude,groupcolumn):
        #分组
        attitudes = pandas.groupby(groupcolumn,as_index=False)[attitude].agg({attitude:'mean'})  #mean秋平均
        return attitudes
    #数据分组 计数
    def atd_count(self,pandas,attitude,groupcolumn):
        #分组
        attitudes = pandas.groupby(groupcolumn,as_index=False)[attitude].agg({attitude:'count'})  #mean秋平均
        return attitudes
    #web data
    def web_data(self,*args,**kwargs):
        result_arr = []
        for item in args[0].index:
            item_arr = []
            item_arr.append(str(args[0].loc[item,args[1]])[0:10])
            for cols in kwargs['columns']:
                item_arr.append('%0.2f'%args[0].loc[item,cols])
            result_arr.append(item_arr)
        return result_arr
