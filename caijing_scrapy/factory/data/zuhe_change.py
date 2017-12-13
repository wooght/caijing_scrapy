#encoding utf-8
# ##################################
# 雪球组合调仓数据组装
# by wooght
# 2017-12
# ##################################
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
from factory.basedata import basedata
import providers.wfunc as wfunc
import os,json
import model.Db as T
import pandas
#获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 601313

class change_data(basedata):

    def select_change(self):
        quotes_data = self.select_quotes(code_id)
        s = T.select([T.zuhe_change]).where(T.zuhe_change.c.code_id==code_id)
        r = T.conn.execute(s)
        if(r.rowcount<1):
            return ''
        data_arr = []
        for i in r.fetchall():
            #数据库查询得到字典
            i = dict(i)
            i['updated_at'] = wfunc.the_day(int(int(i['updated_at'])/1000))
            data_arr.append(i)
        pandas_change = self.pd.DataFrame(data_arr)
        pandas_change['datatime'] = self.pd.to_datetime(pandas_change['updated_at'],format='%Y-%m-%d')
        pd_mean = pandas_change.groupby('datatime',as_index=False)['change_status'].agg({'change_status':'mean'})
        quotes_data['datatime'] = self.pd.to_datetime(quotes_data['datatime'],format='%Y-%m-%d')
        del pandas_change['updated_at']
        pd_mean = self.pd.merge(quotes_data,pd_mean,on=['datatime'],how='left')
        pd_mean = pd_mean.sort_values(by='datatime',ascending=True)
        result = self.web_data(pd_mean,'datatime',columns=['change_status'])
        return result

a = change_data()
b = a.select_change()
print(b)
