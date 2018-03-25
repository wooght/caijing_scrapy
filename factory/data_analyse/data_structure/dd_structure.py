# -*- coding: utf-8 -*-
#
# @method   : 大单/主力数据结构
# @Time     : 2018/2/7
# @Author   : wooght
# @File     : dd_structure.py

import pandas


class dd_structure:
    position = False
    start_kai = []
    pd = pandas
    total_income = 0.

    def f_max_income(self):
        return self.pd.income.max()

    def f_min_income(self):
        return self.pd['income'].min()

    def kai_nums(self):
        pd = self.pd
        return pd[pd['c_state'] == 1].c_state.count()

    def jia_nums(self):
        pd = self.pd
        return pd[pd['c_state'] == 2].c_state.count()

    def income_math(self, day, end_price, is_pull=False, split_index=0):
        income = 0.
        if is_pull: day = day + 1
        start_kai = self.start_kai if split_index == 0 else self.start_kai[:split_index]
        for k in start_kai:
            income += end_price - k
        self.pd.loc[day, 'total_income'] = self.total_income + income
        if is_pull:
            self.total_income += income
        self.pd.loc[day, 'income'] = income
        return income

    def f_total_income(self):
        pd = self.pd
        if self.position:
            last_income = pd.iloc[-1].income
            return self.total_income + last_income
        else:
            return self.total_income


if __name__ == '__main__':
    arr = {
        'position': False,
        'start_kai': [22, 33, 44, 55, 66]
    }
    a = dd_structure()
    a.__dict__ = arr
    print(a.start_kai)
