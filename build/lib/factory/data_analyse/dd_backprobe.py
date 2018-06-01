# -*- coding: utf-8 -*-
#
# @method   : DD Backprobe 过程控制
# @Time     : 2018/2/6
# @Author   : wooght
# @File     : dd_backprobe.py

import os
import sys

sys.path.append(os.path.dirname(__file__)+'/../../')

from ..basedata import basedata
from .dd_position import dd_position
from .dd_math import dd_math
import datetime


class dd_backprobe(basedata):
    dd_position = dd_position()
    dd_math = dd_math()

    range_const = 20  # 范围常数
    rate_const = 0.2  # 速率常数
    times_const = 2  # 速率比例系数

    backprobe_data = object  # 回测数据
    dd_rate = object  # 有变化速率数据
    position = False  # 是否持仓
    income = 0.  # 总收益

    max_income = 0.0  # 最大收益
    min_income = 0.0  # 最大亏损


    #  最后一天做单状态判断
    def last_probe(self, pd_dict):
        sz_pd = self.dd_math.sz_quotes
        last_index = sz_pd.index.max()
        self.dd_position.setdata(pd_dict)
        result = {}
        for d in pd_dict:
            pd = pd_dict[d]
            if self.dd_position.psin(pd.codeid, last_index):
                result[d] = (1, pd.pd.loc[last_index, 'totalvolpct'])
            elif self.dd_position.psout(pd.codeid, last_index) < 0:
                result[d] = (-1, pd.pd.loc[last_index, 'totalvolpct'])
            else:
                result[d] = (0, pd.pd.loc[last_index, 'totalvolpct'])
        return result


    # 回测调度
    # 上证指数为时间基础 遍历每一天,每一只股票
    def dispatch(self, pd_dict, days=0, enddays=0):
        sz_pd = self.dd_math.sz_quotes
        if days != 0:
            maxday = sz_pd['datatime'].max()
            startday = maxday - datetime.timedelta(days=days)
            sz_pd = sz_pd[sz_pd['datatime'] > startday]
        if enddays != 0:
            lastday = sz_pd['datatime'].max()
            endday = lastday - datetime.timedelta(days=days)
            sz_pd = sz_pd[sz_pd['datatime'] < endday]
        self.last_index = sz_pd.index.max()
        start_index = sz_pd.index.min() + self.range_const
        self.dd_position.setdata(pd_dict)
        for i in sz_pd.itertuples():
            if i.Index < start_index or i.Index > self.last_index:
                continue
            for d in pd_dict:
                pd_dict[d] = self.BACKPROBE(i.Index, pd_dict[d])

        return pd_dict

    # 数据回测
    # 加速上升 建仓/加仓 加速下降平仓
    def BACKPROBE(self, day, d):
        shou = d.pd.loc[day, 'shou']
        if d.position:
            # 有单子时候,计算当前收益
            if d.pd.loc[day, 'c_state'] != -1:
                d.income_math(day, shou)
        #  最后一天无法操作下一天
        if day == self.last_index:
            return d
        #  如果停盘,则无任何操作
        if d.pd.loc[day + 1, 'gao'] == 0.00:
            return d
        #  复权判断
        if d.pd.loc[day + 1, 'shou'] - d.pd.loc[day + 1, 'zd_money'] < shou * 4/5:
            if d.position:
                tmp_kai = d.start_kai
                kai_num = d.pd.loc[day + 1, 'kai']
                start_kai = []  # 清空之前开仓数据
                for k in tmp_kai:
                    start_kai.append(kai_num)  # 加入当前开盘为开仓数据
                d.start_kai = start_kai
        #  大于速率常数
        if self.dd_position.psin(d.codeid, day):
            # 主力加速上升 开仓
            # 满足开仓条件,如果已经开仓 及加仓
            d.start_kai.append(d.pd.loc[day+1, 'kai'])
            d.pd.loc[day+1, 'c_state'] = 1 if not d.position else 2  # 2位加仓
            d.position = True
            return d
        if not d.position:
            return d
        # 小于速率常数
        ispc = self.dd_position.psout(d.codeid, day)
        if ispc < 0:
            length = len(d.start_kai)
            if ispc == -2 or length == 1:
                d.position = False
                d.income_math(day, d.pd.loc[day + 1, 'kai'], is_pull=True)
                d.pd.loc[day + 1, 'c_state'] = -1
                d.start_kai = []  # 平仓,清空建仓记录
            elif ispc == -1 and length > 1:
                split_index = round(length/2)
                d.income_math(day, d.pd.loc[day + 1, 'kai'], is_pull=True, split_index=split_index)
                d.pd.loc[day + 1, 'c_state'] = -2  # 部分平仓
                d.start_kai = d.start_kai[split_index:]
        return d


        # pd['total_income'] = pd['total_income'].replace([0, 0.00], method='pad')  # 前值替换
        # self.backprobe_data = pd
        # self.position = position
        # self.income = income

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
    def income_math(self, run_dict, kai, shou):
        income = 0
        # 可能会有多条开仓数据
        for i in kai:
            #  最小操作一手100股
            income += 1 * (shou - i)
        if run_dict.max_income < income:
            run_dict.max_income = income
        elif run_dict.min_income > income:
            run_dict.min_income = income
        return income