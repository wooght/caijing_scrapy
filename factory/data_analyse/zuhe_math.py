# -*- coding: utf-8 -*-
#
# @method   : 组合数据计算
# @Time     : 2018/2/2
# @Author   : wooght
# @File     : zuhe_math.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from common import wfunc
from model import zuhe_change
import pandas as pd
import datetime


class zuhe_math:
    zt32 = 0
    all_data = object

    def select_change(self, code_id, all=False):
        changes = zuhe_change.one(code_id) if not all else zuhe_change.all()
        data_arr = []
        for i in changes:
            # 数据库查询得到字典
            i = dict(i)
            i['updated_at'] = wfunc.the_day(int(int(i['updated_at']) / 1000))
            data_arr.append(i)
        return data_arr

    def user_nums(self, code_id):
        data_arr = self.select_change(code_id)
        df = pd.DataFrame(data_arr)
        df['datatime'] = pd.to_datetime(df['updated_at'])
        del df['updated_at']
        nums_data = df.groupby('datatime', as_index=False)['datatime'].agg({'counts': 'count'})
        return nums_data

    def last100days_mean(self, code_id):
        df = self.user_nums(code_id)
        return df[-100:]['counts'].mean()

    def group_mean(self):
        data_arr = self.select_change(code_id=0, all=True)
        df = pd.DataFrame(data_arr)
        df['datatime'] = pd.to_datetime(df['updated_at'])
        del df['updated_at']
        self.all_data = df
        maxdate = df['datatime'].max()
        startday = maxdate - datetime.timedelta(days=60)  # 获取多少天之前的日期
        last100 = df[df['datatime'] > startday]
        last100 = last100.groupby('code_id', as_index=False)['datatime'].agg({'counts': 'count'})
        last100.sort_values(by='counts', inplace=True)
        the_std = last100['counts'].std()  # 标准差
        self.zt32 = 0.32 * the_std  # 正太分布标准差左边界
        return list(last100[last100['counts'] > self.zt32].code_id)