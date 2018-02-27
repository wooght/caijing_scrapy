# -*- coding: utf-8 -*-
#
# @method   : 大单数据组装
# @Time     : 2018/2/6
# @Author   : wooght
# @File     : dd_math.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from ..basedata import basedata
from model import ddtj
from numpy import floor
from .data_structure.dd_structure import dd_structure


class dd_math(basedata):
    range_const = 20  # 范围常数

    def __init__(self, *args, **kwargs):
        super(dd_math, self).__init__(*args, **kwargs)
        sz_quotes = self.select_quotes(1000001)
        sz_quotes['datatime'] = self.pd.to_datetime(sz_quotes['datatime'])
        sz_quotes = sz_quotes.loc[:, ['datatime']]
        sz_quotes.sort_values(by='datatime', inplace=True)
        sz_quotes.reset_index(inplace=True)
        del sz_quotes['index']
        self.sz_quotes = sz_quotes

    def select_alldd(self):
        all_dd = ddtj.all()
        data_arr = []
        for i in all_dd:
            data_arr.append(dict(i))
        df = self.pd.DataFrame(data_arr)
        df = self.to_math(df, ['totalvolpct', 'kuvolume', 'kdvolume'], ['opendate'])
        return df

    def quotes_install(self, dd_dict):
        for codeid in dd_dict:
            quotes = self.select_quotes(str(codeid))
            obj = self.build_structure(codeid)
            obj.pd = self.mathdata_build(dd_dict[codeid], quotes)
            dd_dict[codeid] = obj
        return dd_dict

    # 数据查询,与行情数据组装
    def one_ddtj(self, code_id):
        # quotes_data = self.select_quotes(code_id)
        dd_data = ddtj.one(code_id)
        data_arr = []
        for i in dd_data:
            # 数据库查询得到字典
            data_arr.append(dict(i))
        pandas_ddtj = self.pd.DataFrame(data_arr)
        pandas_ddtj = self.to_math(pandas_ddtj, ['totalvolpct', 'kuvolume', 'kdvolume'], ['opendate'])
        return pandas_ddtj

    def build_structure(self, codeid):
        obj = dd_structure()
        arr = {
            'codeid': codeid,
            'position': False,
            'start_kai': [],
            'max_income': 0.,
            'min_income': 0.
        }
        obj.__dict__ = arr
        return obj

    def mathdata_build(self, pandas_ddtj, quotes_data):
        pandas_ddtj['datatime'] = self.pd.to_datetime(pandas_ddtj['opendate'], format='%Y-%m-%d')
        pandas_ddtj.drop_duplicates(['datatime'], inplace=True)  # 去重
        pandas_ddtj['dk_contrast'] = pandas_ddtj['kuvolume'] - pandas_ddtj['kdvolume']
        pandas_ddtj['kdvolume'] = -pandas_ddtj['kdvolume']
        quotes_data['datatime'] = self.pd.to_datetime(quotes_data['datatime'], format='%Y-%m-%d')
        del pandas_ddtj['opendate']
        pandas_ddtj = self.pd.merge(quotes_data, pandas_ddtj, on=['datatime'], how='left').fillna(0)
        pandas_ddtj = self.pd.merge(self.sz_quotes, pandas_ddtj, on=['datatime'], how='left').fillna(0)
        # pandas_ddtj.sort_values(by='datatime', ascending=True, inplace=True)  # inplace = True 在原基础上修改
        # pandas_ddtj.reset_index(inplace=True)
        # del pandas_ddtj['index']
        # dk 多空博弈走势
        pandas_ddtj['dk_cumsum'] = pandas_ddtj['dk_contrast'].cumsum()
        pandas_ddtj['dd_change'] = 0  # 大单速率
        pandas_ddtj['shou_change'] = 0  # 收盘速率
        pandas_ddtj['dd_range'] = 0  # 大单范围行程
        pandas_ddtj['shou_range'] = 0  # 大单范围行程
        pandas_ddtj['c_state'] = 0  # 操作状态
        pandas_ddtj['income'] = 0  # 当前结算
        pandas_ddtj['total_income'] = 0.00  # 状态结算
        #  加速度,速率变化值计算
        return self.dd_change(pandas_ddtj)

    # 加速度/速率计算
    def dd_change(self, pd):
        last_index = pd.index.max()
        start_index = pd.index.min() + self.range_const
        pd['shou'] = pd['shou'].replace([0, 0.00], method='pad')
        for i in pd.index:
            # 对行情波动,大单波动进行变化率比较
            # 变化率:在可视范围内,计算变量长度与可视范围长度的比值
            # 可视范围:规定一定日期内的最大值和最小值之差
            if start_index <= i <= last_index:
                start_key = i - self.range_const
                end_key = i  # pd[a:b] 位置取值,不包括后边界 loc[a:b, 'cols'] 索引取值包括后边界
                dd_range = pd.loc[start_key:end_key, 'dk_cumsum'].max() - pd.loc[start_key:end_key, 'dk_cumsum'].min()
                pd.loc[i, 'dd_range'] = dd_range
                shou_range = pd.loc[start_key:end_key, 'shou'].max() - pd.loc[start_key:end_key, 'shou'].min()
                pd.loc[i, 'shou_range'] = shou_range
                dd_change = pd.loc[i, 'dk_contrast'] / dd_range if dd_range > 0 else 0
                pd.loc[i, 'dd_change'] = floor(100 * dd_change) / 100
                shou_change = pd.loc[i, 'zd_money'] / shou_range if shou_range > 0 else 0
                pd.loc[i, 'shou_change'] = floor(100 * shou_change) / 100
        return pd
