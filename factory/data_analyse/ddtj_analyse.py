# -*- coding: utf-8 -*-
#
# @method   : 大单回测算法-速率变化
# @Time     : 2018/1/18
# @Author   : wooght
# @File     : ddtj_analyse.py

import os
import sys

sys.path.append(os.path.dirname(__file__)+'/../../')

from ..basedata import basedata
from .dd_position import dd_position
from model import ddtj
from numpy import floor


class ddtj_analyse(basedata):
    dd_position = dd_position()

    range_const = 20  # 范围常数
    rate_const = 0.2  # 速率常数
    times_const = 2  # 速率比例系数

    backprobe_data = object  # 回测数据
    dd_rate = object  # 有变化速率数据
    position = False  # 是否持仓
    income = 0.  # 总收益

    max_income = 0.0  # 最大收益
    min_income = 0.0  # 最大亏损

    # 数据查询,与行情数据组装
    def select_ddtj(self, code_id, start_date='2015-01-01'):
        quotes_data = self.select_quotes(code_id)
        dd_repository = ddtj.one(code_id)
        data_arr = []
        for i in dd_repository:
            # 数据库查询得到字典
            data_arr.append(dict(i))
        pandas_ddtj = self.pd.DataFrame(data_arr)
        pandas_ddtj['datatime'] = self.pd.to_datetime(pandas_ddtj['opendate'], format='%Y-%m-%d')
        pandas_ddtj['dk_contrast'] = pandas_ddtj['kuvolume'] - pandas_ddtj['kdvolume']
        pandas_ddtj['kdvolume'] = -pandas_ddtj['kdvolume']
        quotes_data['datatime'] = self.pd.to_datetime(quotes_data['datatime'], format='%Y-%m-%d')
        del pandas_ddtj['opendate']
        pandas_ddtj = self.pd.merge(quotes_data, pandas_ddtj, on=['datatime'], how='left').fillna(0)
        pandas_ddtj.sort_values(by='datatime', ascending=True, inplace=True)  # inplace = True 在原基础上修改
        pandas_ddtj.reset_index(inplace=True)
        del pandas_ddtj['index']
        pandas_ddtj['dk_cumsum'] = pandas_ddtj['dk_contrast'].cumsum()
        pandas_ddtj['dd_change'] = 0  # 大单速率
        pandas_ddtj['shou_change'] = 0  # 收盘速率
        pandas_ddtj['dd_range'] = 0  # 大单范围行程
        pandas_ddtj['shou_range'] = 0  # 大单范围行程
        # print(pandas_ddtj.loc[:,['dk_contrast','shou','dk_cumsum','zd_money','datatime']])
        # pandas_ddtj = pandas_ddtj[pandas_ddtj['datatime'] > start_date]
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
        self.dd_rate = pd


    #  最后一天做单状态判断
    def last_probe(self):
        last_index = self.dd_rate.index.max()
        self.dd_position.setdata(self.dd_rate)
        if self.dd_position.psin(last_index):
            return (1, self.dd_rate.loc[last_index, 'totalvolpct'])
        elif self.dd_position.psout(last_index, is_times=True):
            return (-1, self.dd_rate.loc[last_index, 'totalvolpct'])
        else:
            return (0, self.dd_rate.loc[last_index, 'totalvolpct'])


    # 数据回测
    # 加速上升 建仓/加仓 加速下降平仓
    def BACKPROBE(self, is_times):
        pd = self.dd_rate
        pd['c_state'] = 0
        pd['income'] = 0.00
        last_index = pd.index.max()
        start_index = pd.index.min() + self.range_const
        position = False  # 当前是否有仓位
        start_kai = []  # 开仓点位
        income = 0.  # 收益
        self.max_income = 0.
        self.min_income = 0.
        pd['shou'].astype(float)
        pd['kai'] = self.pd.to_numeric(pd['kai'])
        pd['before'] = self.pd.to_numeric(pd['before'])
        pd['total_income'] = 0  #总收益
        self.dd_position.setdata(pd)
        for i in pd.itertuples():
            if start_index <= i.Index <= last_index:
                # print(start_index, i.Index, last_index)
                if position:
                    # 有单子时候,计算当前收益
                    if pd.loc[i.Index, 'c_state'] != -1:
                        in_tmp = self.income_math(start_kai, i.shou)
                        pd.loc[i.Index, 'income'] = in_tmp
                        pd.loc[i.Index, 'total_income'] = income+in_tmp
                #  最后一天无法操作下一天
                if i.Index == last_index:
                    break
                #  如果停盘,则无任何操作
                if pd.loc[i.Index + 1, 'gao'] == 0.00:
                    continue
                #  复权判断
                if pd.loc[i.Index + 1, 'shou'] - pd.loc[i.Index + 1, 'zd_money'] < i.shou * 4/5:
                    in_tmp = self.income_math(start_kai, i.shou)
                    income += in_tmp
                    tmp_kai = start_kai
                    kai_num = pd.loc[i.Index + 1, 'kai']
                    start_kai = []  # 清楚之前开仓数据
                    for k in tmp_kai:
                        start_kai.append(kai_num)  # 加入当前开盘为开仓数据
                #  大于速率常数
                if self.dd_position.psin(i.Index):
                    # 主力加速上升 开仓
                    # 满足开仓条件,如果已经开仓 及加仓
                    start_kai.append(pd.loc[i.Index+1, 'kai'])
                    pd.loc[i.Index+1, 'c_state'] = 1 if not position else 2  # 2位加仓
                    position = True
                    continue
                if not position:
                    continue
                # 小于速率常数
                ispc = self.dd_position.psout(i.Index, is_times)
                if ispc < 0:
                    length = len(start_kai)
                    if ispc == -1 and length > 1:
                        split_index = round(length/2)
                        income_pc = self.income_math(start_kai[:split_index], pd.loc[i.Index+1, 'kai'])
                        income += income_pc
                        pd.loc[i.Index+1, 'c_state'] = -2  # 部分平仓
                        pd.loc[i.Index+1, 'income'] = income_pc
                        start_kai = start_kai[split_index:]
                    elif ispc == -2:
                        position = False
                        income_tmp = self.income_math(start_kai, pd.loc[i.Index+1, 'kai'])
                        income += income_tmp
                        pd.loc[i.Index+1, 'c_state'] = -1
                        pd.loc[i.Index+1, 'income'] = income_tmp
                        pd.loc[i.Index+1, 'total_income'] = income
                        start_kai = []  # 平仓,清空建仓记录

        pd['total_income'] = pd['total_income'].replace([0, 0.00], method='pad')  # 前值替换
        self.backprobe_data = pd
        self.position = position
        self.income = income

    def web_api(self):
        dd_data = self.web_data(self.backprobe_data, 'datatime', columns=['shou', 'dk_cumsum', 'totalvolpct',
                                                        'c_state', 'income', 'dd_change', 'shou_change', 'total_income'])
        hc_position = []  # [[开时间,收盘],[平时间,收盘],收益],
        hc_status = []
        hc_jia = []  # [时间,收盘],
        for i in dd_data:
            if float(i[4]) == 1.00:
                hc_status = [i[0], i[1]]
            elif float(i[4]) == -1.00:
                hc_position.append([hc_status, [i[0], i[1]], i[5]])
            elif float(i[4]) == -2.0:
                hc_position.append([hc_status, [i[0], i[1]], i[5]])
                hc_status = [i[0], i[1]]
            elif float(i[4]) == 2.0:
                hc_jia.append([i[0], i[1]])
        if self.position:
            hc_position.append([hc_status, [dd_data[-1][0], dd_data[-1][1]], dd_data[-1][5]])
            now_income = self.income + float(dd_data[-1][5])
        else: now_income = self.income
        re_data = {
            'dd_data': dd_data,  # 行情/大单数据
            'hc': hc_position,  # 回测数据
            'income': now_income,  # 总收益数据
            'jia_num': self.backprobe_data[self.backprobe_data.c_state == 2].c_state.count(),  # 筛选c_state为2的数量
            'hc_jia': hc_jia,  # 加仓数据
            'max_income': {'max': self.max_income, 'min': self.min_income}  # 最大收/亏
        }
        return re_data


    # 平仓收益计算
    def income_math(self, kai, shou):
        income = 0
        # 可能会有多条开仓数据
        for i in kai:
            #  最小操作一手100股
            income += 1 * (shou - i)
        if self.max_income < income:
            self.max_income = income
        elif self.min_income > income:
            self.min_income = income
        return income