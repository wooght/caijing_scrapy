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
        self.ddpct_mean = pd['totalvolpct'].mean()

    def psin(self, i):
        if self.pct_mean(i) < 0.3: return False
        shou_change = self.pd.loc[i, 'shou_change']
        dd_change = self.pd.loc[i, 'dd_change']
        #  大于速率常数且走势为正
        if dd_change > self.rate_const and shou_change > 0:
            times_rate = self.times_const * self.rate_const
            now_times_shou = self.times_const * shou_change
            now_pct_mean = self.pd.loc[i, 'totalvolpct']
            both_like = dd_change > shou_change or self.both_like(dd_change, shou_change)
            than_rate = dd_change >= now_times_shou if now_pct_mean >= 0.5 else both_like  # 速率大于走势*系数
            than_const = dd_change >= times_rate and both_like  # 速率大于速率常数,且大于走势
            return than_rate or than_const
        else:
            return False

    def psout(self, i, is_times):
        dd_change = self.pd.loc[i, 'dd_change']
        if self.pd.loc[i, 'zd_range'] <= -9.9:
            # 出现跌停
            return -2
        if self.down_continue5(i):
            return -2
        # 小于速率常数
        if dd_change < -self.rate_const:
            # 主力加速下降 平仓
            # 和速率常数相比,前提是和行情速率相比成立
            shou_change = self.pd.loc[i, 'shou_change']
            now_pct_mean = self.pd.loc[i, 'totalvolpct']
            now_times_shou = self.times_const * shou_change
            times_rate = -self.times_const * self.rate_const
            # 大单占比小于0.5的,减小带动指数
            sc_tmp = now_times_shou if now_pct_mean >= 0.5 else 2 / 3 * now_times_shou
            than_rate = dd_change < sc_tmp  # 小于走势速率
            than_const = dd_change < times_rate and (
                    dd_change < shou_change or self.both_like(dd_change, shou_change))  # 小于速率常数,且小于走势
            # ismaxliang = self.pd.loc[i]['liang'] >= self.pd.loc[i - self.range_const:i, 'liang'].max()  # 大成交量
            # ismaxrange = self.pd.loc[i]['zd_money'] <= self.pd.loc[i - self.range_const:i, 'zd_money'].min()  # 最大降幅
            # than_liang_money = ismaxliang and ismaxrange
            if than_rate and than_const:
                return -2
            elif than_rate or than_const:
                return -1
            else:
                return 1
        else:
            return 1

    # 范围占比均值计算
    def pct_mean(self, i):
        #  暂时设定大于0.4
        return self.pd.loc[i - self.range_const:i, 'totalvolpct'].mean()

    # 两者相当
    def both_like(self, d, s):
        if d * s < 0:
            return False
        dd = abs(d)
        shou = abs(s)
        if dd > shou:
            return shou > dd * 0.9
        elif shou > dd:
            return dd > shou * 0.9

    # 双双连续缓慢下跌
    def down_continue5(self, i):
        dd = self.pd.loc[i - 4:i, 'dd_change'].max() < 0
        shou = self.pd.loc[i - 4:i, 'shou_change'].max() < 0
        return dd and shou