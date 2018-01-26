# -*- coding: utf-8 -*-
#
# @method   : 进出场判断
# @Time     : 2018/1/24
# @Author   : wooght
# @File     : dd_position.py


class dd_position:
    rate_const = 0.2  # 速率常数
    times_const = 2  # 速率比例系数
    range_const = 20  # 范围常数
    pd = object

    def setdata(self, pd):
        self.pd = pd

    def psin(self, i):
        if not self.pct_mean(i): return False
        shou_change = self.pd.loc[i, 'shou_change']
        dd_change = self.pd.loc[i, 'dd_change']
        #  大于速率常数且走势为正
        if dd_change > self.rate_const and shou_change > 0:
            than_rate = dd_change >= self.times_const * shou_change  # 速率大于走势*系数
            than_const = dd_change >= self.times_const * self.rate_const and dd_change > shou_change  # 速率大于速率常数,且大于走势
            return than_rate or than_const
        else:
            return False

    def psout(self, i, is_times):
        dd_change = self.pd.loc[i, 'dd_change']
        #  小于速率常数
        if dd_change < -self.rate_const:
            # 主力加速下降 平仓
            # 和行情速率相比,分不乘以系数,和乘以系数
            # 和速率常数相比,前提是和行情速率相比成立
            shou_change = self.pd.loc[i, 'shou_change']
            sc_tmp = self.times_const * shou_change if is_times else shou_change
            than_rate = dd_change < sc_tmp  # 小于走势速率
            than_const = dd_change < -self.times_const * self.rate_const and dd_change < shou_change  # 小于速率常数,且小于走势
            return than_const or than_rate
        else:
            return False

    # 范围占比均值计算
    def pct_mean(self, i):
        #  暂时设定大于0.4
        return self.pd.loc[i - self.range_const:i, 'totalvolpct'].mean() > 0.3
