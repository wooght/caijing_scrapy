# -*- coding:utf-8 -*-
# #######################
# quotes 行情仓库
# by Wooght
# date 2017-12-25
# #######################

from ..Db import *
import json

class Table_quotes():
    table = quotes_item
    cols = table.c

    #存在大于0的行情
    def exists_quotes(self,id=0):
        if(id>0):
            s = self.select_quotes('quotes','code_id',code_id=id)
        else:
            s = self.select_quotes('quotes','code_id')
        code = []
        for quotes in s.fetchall():
            quotes_json = json.loads(quotes[0])
            one = []
            one.append(quotes[1])
            opendate = []
            for dateitem in quotes_json:
                if(float(dateitem['shou'])>0):
                    #行情收大于0 没停盘的才有效
                    opendate.append(dateitem['datatime'])
            one.append(opendate)
            code.append(one)
        # return [codeid,[quotes]]
        return code
    def select_quotes(self,*args,**kwargs):
        columns = []
        for col in args:
            columns.append(self.cols[col])
        r = select(columns)
        if('code_id' in kwargs):
            r = r.where(self.cols['code_id']==kwargs['code_id'])
        s = conn.execute(r)
        return s
