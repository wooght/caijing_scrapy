# -*- coding: utf-8 -*-
#
# @method   : 大单回测算法-速率变化
# @Time     : 2018/1/18
# @Author   : wooght
# @File     : ddtj_analyse.py

import sys
from data_config import sys_path

sys.path.append(sys_path)

from factory.basedata import basedata
from model import T
from numpy import floor

# 获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 776


class ddtj_analyse(basedata):

    range_const = 20  # 范围常数
    rate_const = 0.2  # 速率常数
    times_const = 2  # 速率比例常数

    def select_ddtj(self):
        quotes_data = self.select_quotes(code_id)
        s = T.select([T.ddtj.c.totalamt, T.ddtj.c.totalamtpct, T.ddtj.c.totalvol, T.ddtj.c.totalvolpct,
                      T.ddtj.c.stockvol, T.ddtj.c.stockamt, T.ddtj.c.opendate, T.ddtj.c.kuvolume,
                      T.ddtj.c.kdvolume]).where(T.ddtj.c.code_id == code_id)
        r = T.conn.execute(s)
        data_arr = []
        for i in r.fetchall():
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
        pandas_ddtj['dd_change'] = 0
        pandas_ddtj['shou_change'] = 0
        pandas_ddtj['dd_range'] = 0
        pandas_ddtj['shou_range'] = 0
        # print(pandas_ddtj.loc[:,['dk_contrast','shou','dk_cumsum','zd_money','datatime']])
        return self.dd_change(pandas_ddtj)


    # 范围速率计算
    def dd_change(self, pd):
        count_num = pd.datatime.count()
        pd['shou'] = pd['shou'].replace([0, 0.00], method='pad')
        for i in pd.index:
            # 对行情波动,大单波动进行变化率比较
            # 变化率:在可视范围内,计算变量长度与可视范围长度的比值
            # 可视范围:规定一定日期内的最大值和最小值之差
            if self.range_const <= i < count_num:
                dd_range = pd['dk_cumsum'][i - self.range_const:i].max() - pd['dk_cumsum'][
                                                                               i - self.range_const:i].min()
                pd.loc[i, 'dd_range'] = dd_range
                shou_range = pd['shou'][i - self.range_const:i].max() - pd['shou'][i - self.range_const:i].min()
                pd.loc[i, 'shou_range'] = shou_range
                dd_change = pd.loc[i, 'dk_contrast'] / dd_range
                pd.loc[i, 'dd_change'] = floor(100 * dd_change) / 100
                shou_change = pd.loc[i, 'zd_money'] / shou_range
                pd.loc[i, 'shou_change'] = floor(100 * shou_change) / 100
        self.dd_range = pd

    # 数据回测
    def BACKPROBE(self, is_times):
        pd = self.dd_range
        pd['c_state'] = 0
        pd['income'] = 0
        count_num = pd.datatime.count()
        position = False  # 当前是否有仓位
        start_kai = []  # 开仓点位
        income = 0.  # 收益
        pd['shou'].astype(float)
        pd['kai'] = self.pd.to_numeric(pd['kai'])
        pd['total_income'] = 0  #总收益
        for i in pd.itertuples():
            if self.range_const <= i.Index < count_num:
                if position:
                    # 有单子时候,计算当前收益
                    if pd.loc[i.Index, 'c_state'] != -1:
                        in_tmp = self.income_math(start_kai, i.shou)
                        pd.loc[i.Index, 'income'] = in_tmp
                        pd.loc[i.Index, 'total_income'] = income+in_tmp
                #  最后一天无法操作下一天
                if i.Index == count_num-1:
                    break
                # 大于速率常数
                if i.dd_change > self.rate_const:
                    # 主力加速上升 开仓
                    than_rate = i.dd_change >= self.times_const * i.shou_change  # 速率大于走势
                    than_const = i.dd_change >= self.times_const * self.rate_const  # 速率大于绝对常数
                    if than_rate or than_const:
                        start_kai.append(pd.loc[i.Index+1, 'kai'])
                        pd.loc[i.Index+1, 'c_state'] = 1 if not position else 2  # 2位加仓
                        position = True
                # 小于速率常数
                elif i.dd_change < -self.rate_const:
                    if not position:
                        continue
                    # 主力加速下降 平仓
                    sc_tmp = self.times_const * i.shou_change if is_times else i.shou_change
                    than_rate = i.dd_change < sc_tmp
                    than_const = i.dd_change < -self.times_const * self.rate_const
                    if than_const or than_rate:
                        #  平仓
                        position = False
                        income_tmp = self.income_math(start_kai, pd.loc[i.Index+1, 'kai'])
                        income += income_tmp
                        pd.loc[i.Index+1, 'c_state'] = -1
                        pd.loc[i.Index+1, 'income'] = income_tmp
                        pd.loc[i.Index+1, 'total_income'] = income
                        start_kai = []  # 平仓,清空建仓记录
        pd['total_income'] = pd['total_income'].replace([0, 0.00], method='pad')  # 前值替换
        dd_data = self.web_data(pd, 'datatime', columns=['shou', 'dk_cumsum', 'totalvolpct',
                                                        'c_state', 'income', 'dd_change', 'shou_change', 'total_income'])
        hc_position = []
        hc_status = []
        hc_jia = []
        for i in dd_data:
            if float(i[4]) == 1.00:
                hc_status = [i[0], i[1]]
            elif float(i[4]) == -1.00:
                hc_position.append([hc_status, [i[0], i[1]], i[5]])
            elif float(i[4]) == 2.0:
                hc_jia.append([i[0], i[1]])
        if position:
            hc_position.append([hc_status, [dd_data[-1][0], dd_data[-1][1]], dd_data[-1][5]])
            income += float(dd_data[-1][5])
        re_data = {
            'dd_data': dd_data,
            'hc': hc_position,
            'income': income,
            'jia_num': pd[pd.c_state == 2].c_state.count(),  # 筛选c_state为2的数量
            'hc_jia': hc_jia
        }
        return re_data


    # 平仓收益计算
    def income_math(self, kai, shou):
        income = 0
        for i in kai:
            income += shou - i
        return income


dd = ddtj_analyse()
dd.select_ddtj()
is_times = dd.BACKPROBE(True)
no_times = dd.BACKPROBE(False)
result = {
    'is_data': is_times,
    'is_nums': len(is_times['hc']),
    'is_income': floor(is_times['income']*100)/100,
    'is_jia': is_times['jia_num'],
    'no_nums': len(no_times['hc']),
    'no_income': floor(no_times['income']*100)/100,
    'no_jia': no_times['jia_num'],
}
print(result)

# for i in is_times['dd_data']:
#     print(i)