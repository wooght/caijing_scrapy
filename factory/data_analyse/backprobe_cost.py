# -*- coding: utf-8 -*-
#
# @method   : 回测费用控制
# @Time     : 2018/2/3
# @Author   : wooght
# @File     : backprobe_cost.py


class backprobe_cost:
    spend = 0  # 花费
    capital = 0  # 可用资金
    base_rate = 0  # 默认成本比例

    def __init__(self, capital=100000, base_rate=0.008):
        self.capital = capital
        self.base_rate = base_rate


    # 手续费计算
    def revenue(self, price, stock_num):
        return price * stock_num * self.base_rate


    # 开始计费
    def start_cost(self, price, stock_num):
        pay = price * stock_num + self.revenue(price, stock_num)
        if self.capital - pay > 0:
            self.capital -= pay
            return True
        else:
            return False


    # 结束计费
    def end_cost(self, price, stock_num):
        pay = price * stock_num - self.revenue(price, stock_num)
        self.capital += pay
        return self.capital