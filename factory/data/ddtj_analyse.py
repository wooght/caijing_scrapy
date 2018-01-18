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
    code_id = 2


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


    def dd_change(self, pd):
        count_num = pd.datatime.count()
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
        return self.BACKPROBE(pd)

    # 数据回测
    def BACKPROBE(self, pd):
        pd['c_state'] = 0
        pd['income'] = 0
        count_num = pd.datatime.count()
        position = False  # 当前是否有仓位
        start_kai = 0.  # 开仓点位
        income = 0.  # 收益
        pd['shou'].astype(float)
        pd['kai'] = self.pd.to_numeric(pd['kai'])
        for i in pd.itertuples():
            if self.range_const <= i.Index < count_num:
                if position:
                    if pd.loc[i.Index, 'c_state'] == 0:
                        pd.loc[i.Index, 'income'] = i.shou - start_kai
                # 大于速率常数
                if i.dd_change > self.rate_const:
                    if position:
                        continue
                    # 主力加速上升 开仓
                    if i.dd_change > self.times_const * i.shou_change:
                        position = True
                        start_kai = pd.loc[i.Index+1, 'kai']
                        pd.loc[i.Index+1, 'c_state'] = 1
                # 小于速率常数
                elif i.dd_change < -self.rate_const:
                    # 主力加速下降 平仓
                    if i.dd_change < self.times_const * i.shou_change:
                        if not position:
                            continue
                        else:
                            position = False
                            income_tmp = pd.loc[i.Index+1, 'kai'] - start_kai
                            income += income_tmp
                            pd.loc[i.Index+1, 'c_state'] = -1
                            pd.loc[i.Index+1, 'income'] = income_tmp
        # for i in pd.itertuples():
        #     print(i.datatime, '\t', i.dd_change, '\t', i.shou_change, '\t', i.c_state, '\t', i.income)
        # print(income, position)
        dd_data = self.web_data(pd, 'datatime', columns=['shou', 'dk_cumsum', 'totalvolpct',
                                                                 'c_state', 'income'])
        result_hc = []
        hc_status = []
        for i in dd_data:
            if float(i[4]) == 1.00:
                hc_status = [i[0], i[1]]
            elif float(i[4]) == -1.00:
                result_hc.append([hc_status, [i[0], i[1]], i[5]])
        if position:
            result_hc.append([hc_status, [dd_data[-1][0], dd_data[-1][1]], dd_data[-1][5]])
        result = {
            'dd_data': dd_data,
            'hc': result_hc
        }
        return result








a = ddtj_analyse()
b = a.select_ddtj()
print(b)